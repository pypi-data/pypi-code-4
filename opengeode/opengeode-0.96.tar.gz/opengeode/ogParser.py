#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
    OpenGEODE SDL92 parser

    This library builds the SDL AST (described in ogAST.py)
    The AST can then be used to build SDL backends such as the
    diagram editor (placing symbols in a graphical canvas for editition)
    or code generators, etc.

    The AST build is based on the ANTLR-grammar and generated lexer and parser
    (the grammar is in the file sdl92.g and requires antlr 3.1.3 for Python
    to be compiled and used).

    During the build of the AST this library makes a number of semantic
    checks on the SDL input mode.

    Copyright (c) 2012-2013 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__author__ = 'Maxime Perrotin'

import sys
import os
import importlib
import logging
#import traceback
import antlr3
import antlr3.tree

import sdl92Lexer as lexer
from sdl92Parser import sdl92Parser

import samnmax
import ogAST

LOG = logging.getLogger(__name__)

OPKIND = {lexer.PLUS: 'plus',
          lexer.ASTERISK: 'mul',
          lexer.DASH: 'minus',
          lexer.OR: 'or',
          lexer.AND: 'and',
          lexer.XOR: 'xor',
          lexer.EQ: 'eq',
          lexer.NEQ: 'neq',
          lexer.GT: 'gt',
          lexer.GE: 'ge',
          lexer.LT: 'lt',
          lexer.LE: 'le',
          lexer.DIV: 'div',
          lexer.MOD: 'mod',
          lexer.APPEND: 'append',
          lexer.IN: 'in',
          lexer.REM: 'rem',
          lexer.PRIMARY: 'primary'}

# Insert current path in the search list for importing modules
sys.path.insert(0, '.')

DV = None

# Code generator backends may need some intemediate variables to process
# expressions. For convenience and to avoid multiple pass parsing, the parser
# tries to guess where they may be useful, and adds a hint in the AST.
TMPVAR = 0

# Special SDL operators
SPECIAL_OPERATORS = ['length', 'write', 'writeln', 'present', 'set_timer',
        'reset_timer']

UNKNOWN_TYPE = type('UnknownType', (object,), {'kind': 'UnknownType'})

# Shortcut to create a new referenced ASN.1 type
new_ref_type = lambda refname: \
        type(str(refname), (object,),
                {'kind': 'ReferenceType',
                 'ReferencedTypeName': refname.replace('_', '-')})

# Shortcut to return a type name (Reference name or basic type)
type_name = lambda t: \
                t.kind if t.kind != 'ReferenceType' else t.ReferencedTypeName

types = lambda: getattr(DV, 'types', {})


def sdl_to_asn1(sort):
    '''
        Convert case insensitive type reference to the actual type as found
        in the ASN.1 datamodel
    '''
    for asn1_type in types().viewkeys():
        if sort.replace('_', '-').lower() == asn1_type.lower():
            break
    else:
        raise TypeError('Type {} not found in ASN.1 model'.format(sort))
    return new_ref_type(asn1_type)


def node_filename(node):
    ''' Return the filename associated to the stream of this node '''
    parent = node
    while parent:
        try:
            return parent.getToken().getInputStream().fileName
        except AttributeError:
            parent = parent.getParent()
    return None


def token_stream(node):
    '''
        Return the token stream associated to a tree node
        It is set at the root of the tree by the parser
    '''
    parent = node
    while parent:
        try:
            return parent.token_stream
        except AttributeError:
            parent = parent.getParent()


def signals_in_system(ast):
    ''' Recursively find signal definitions in a nested SDL model '''
    all_signals = []
    for block in ast.blocks:
        all_signals.extend(signals_in_system(block))
    all_signals.extend(ast.signals)
    return all_signals


def find_process_declaration(ast, process_name):
    ''' Recursively search for a process declaration in a nested SDL model '''
    for block in ast.blocks:
        result = find_process_declaration(block, process_name)
        if result:
            return result
    try:
        for process in ast.processes:
            if process.processName == process_name:
                return process
    except AttributeError:
        return None
    return None


def valid_output(scope):
    '''
        Yields the output, procedures, and operators names,
        that is all the elements that can be valid in an OUTPUT symbol
        (does not mean it IS valid - caller still has to check it)
    '''
    for out_sig in scope.output_signals:
        yield out_sig['name'].lower()
    for proc in scope.procedures:
        yield proc.inputString.lower()
    for special_op in SPECIAL_OPERATORS:
        yield special_op.lower()
    for inner_proc in scope.content.inner_procedures:
        yield inner_proc.inputString.lower()


def get_interfaces(ast, process_name):
    '''
        Search for the list of input and output signals (async PI/RI)
        and procedures (sync RI) of a process in a given top-level AST
    '''
    all_signals = []
    async_signals = []
    system = None

    # Move up to the system level, in case process is nested in a block
    # and not defined at root level as it is the case when it is referenced
    system = ast
    while hasattr(system, 'parent'):
        system = system.parent

    # If we are at AST level, check in all systems, otherwise in current one
    iterator = ast.systems if hasattr(ast, 'systems') else (system,)

    for system in iterator:
        all_signals.extend(signals_in_system(system))
        process_ref = find_process_declaration(system, process_name)
        if process_ref:
            break
    else:
        if isinstance(ast, ogAST.Block):
            process_ref = ast
        else:
            raise TypeError('Process ' + process_name +
                        ' is defined but not not declared in a system')
    # Go to the block where the process is defined
    process_parent = process_ref.parent
    # Find in and out signals names using the signalroutes
    for signalroute in process_parent.signalroutes:
        for route in signalroute['routes']:
            if route['source'] == process_name:
                direction = 'out'
            elif route['dest'] == process_name:
                direction = 'in'
            else:
                continue
            for sig_id in route['signals']:
                # Copy the signal to the result dict
                found, = [dict(sig) for sig in all_signals
                          if sig['name'] == sig_id]
                found['direction'] = direction
                async_signals.append(found)
    return async_signals, system.procedures


def get_input_string(root):
    ''' Return the input string of a tree node '''
    return token_stream(root).toString(root.getTokenStartIndex(),
            root.getTokenStopIndex())


def get_state_list(process_root):
    ''' Return the list of states of a process '''
    # 1) get all STATE statements
    states = (child for child in process_root.getChildren()
            if child.type == lexer.STATE)
    # 2) keep only the ones containing a STATELIST token (i.e. no ASTERISK)
    relevant = (child for state in states for child in state.getChildren()
            if child.type == lexer.STATELIST)
    # 3) extract the state list from each of them
    state_list = [s.text.lower() for r in relevant for s in r.getChildren()]
    # state_list.append('START')
    # 4) create a set to remove duplicates
    return set(state_list)


def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of a_type '''
    basic_type = a_type or UNKNOWN_TYPE
    while basic_type.kind == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in types().viewkeys():
            if typename.lower() == basic_type.ReferencedTypeName.lower():
                basic_type = types()[typename].type
                break
        else:
            raise TypeError('Type "' + type_name(basic_type) +
                            '" was not found in Dataview')
    return basic_type


def is_constant(var):
    ''' Check in ASN.1 modules if var (Primary) is declared as a constant '''
    if var is None:
        return False
    if var.kind == 'constant':
        return True
    if DV and var.kind == 'primaryId':
        for mod in DV.asn1Modules:
            for constant in DV.exportedVariables[mod]:
                if(constant.lower() ==
                                  var.primaryId[0].lower().replace('_', '-')):
                    LOG.debug('Constant ' + var.inputString + ' found')
                    return True
    return False


def check_and_fix_op_params(op_name, expr_list, context):
    '''
        Verify and/or set the type of a procedure/output parameters
        TODO: when supported, add operators
    '''
    # (1) Find the signature of the function
    # signature will hold the list of parameters for the function
    LOG.debug('[check_and_fix_op_params] ' + op_name + ' - ' + str(expr_list))
    signature = []
    key = ''

    for out_sig in context.output_signals:
        if out_sig['name'].lower() == op_name.lower():
            if out_sig.get('type'):
                # output signals: one single parameter
                signature = [{'type': out_sig.get('type'),
                              'name': out_sig.get('param_name' or ''),
                              'direction': 'in'}]
            break
    else:
        # Procedures (inner and external)
        for inner_proc in (context.content.inner_procedures 
                           + context.procedures):
            key = inner_proc.inputString
            if key.lower() == op_name.lower():
                signature = inner_proc.fpar
                break
        else:
            if op_name.lower() not in SPECIAL_OPERATORS:
                raise AttributeError('Operator/output/procedure not found: '
                    + op_name)
            else:
                # Special operators: parameters are context dependent,
                # so we set signature to None to avoid further tests
                signature = None
    # (2) Check that the number of given parameters matches the signature
    if signature is not None and len(signature) != len(expr_list):
        raise TypeError('Wrong number of parameters')
    # (3) Check each individual parameter type
    for idx, param in enumerate(expr_list):
        # Get parameter type from the function signature:
        if signature is not None:
            param_type = signature[idx].get('type').ReferencedTypeName
            # Retrieve the type (or None if it is a sepecial operator)
            dataview_entry = types().get(param_type) or UNKNOWN_TYPE
            dataview_type = dataview_entry.type

        # Try to set the type of the user expression if it is missing
        # This is needed because some internal SDL operators (Length, Present)
        # work on a type that is not fixed. In that case we must look in the
        # list of variables to get the type of the expression set by the user
        if param.exprType.kind == 'UnknownType':
            # Look in the list of variables
            # TODO: we should exclude enumerated types here
            try:
                param.exprType = find_variable(param.inputString, context)
            except AttributeError:
                # If type is still unknown, copy it from the signature:
                # (except for special operators, that have non-fixed types)
                if signature is not None:
                    param.exprType = new_ref_type(param_type)
                else:
                    raise TypeError('Unable to determine param type: ' +
                          param.inputString + '(in operator ' + op_name + ')')
        # If expr is a terminal primary, check for type compatibility
        if param.is_raw() and signature is not None:
            if not isOfCompatibleType(param.var, dataview_type, context):
                LOG.debug('[Check_and_fix_op_params] Incompatible types')
                raise AttributeError('Param ' + signature[idx].get('name') +
                        ' has a type incompatibility with ' + param_type)
        # Finally, compare the two types (param.exprType and signature type)
        if signature is not None and not compare_types(
                                        dataview_type, param.exprType):
            LOG.debug('[Check_and_fix_op_params] Compare type returned false')
            raise AttributeError('Param ' + signature[idx].get('name') +
                    ' is not of type ' + param_type)
        else:
            if signature is not None and param.kind == 'primary':
                # If param type is OK and primary type, propagate the type
                # of the expression to the primary (useful for Strings)
                #param.var.primType = dataview_type
                # Update MP 05-11-2013: we need a ref type for code generation
                param.var.primType = new_ref_type(param_type)


def isOfCompatibleType(primary, typeRef, context):
    '''
        Check if a primary (raw value, enumerated, ASN.1 Value...)
        is compatible with a given type
    '''
    assert typeRef is not None
    if primary.kind == 'constant':
        return True
    try:
        actual_type = find_basic_type(typeRef)
    except TypeError as err:
        LOG.error(str(err))
        return False
    logmsg = ("[isOfCompatibleType] checking if {value} is of type {typeref}: "
              .format(value=primary.inputString, typeref=actual_type.kind))

    if (primary.kind == 'primaryId'
            and actual_type.kind.endswith('EnumeratedType')):
        # If type ref is an enumeration, check that the value is valid
        # Note, when using the "present" operator of a CHOICE type, the
        # resulting value is actually an EnumeratedType
        enumerant = primary.primaryId[0].replace('_', '-')
        corr_type = actual_type.EnumValues.get(enumerant)
        if corr_type:
            # enumeratedValue/choiceDeterminant kinds can only be set here
            if actual_type.kind == 'ChoiceEnumeratedType':
                primary.kind = 'choiceDeterminant'
                primary.primType = actual_type
            else:
                primary.kind = 'enumeratedValue'
                primary.primType = actual_type
            LOG.debug(logmsg + 'YES')
            return True
        else:
            LOG.debug(logmsg + 'NO: Value "' + primary.primaryId[0] +
                   '"not in this enumeration:' + actual_type.EnumValues.keys())
            return False
    elif(primary.kind == 'primaryId' and len(primary.primaryId) == 1 and
            primary.primType.kind == 'UnknownType'):
        try:
            primary.primType = find_variable(primary.primaryId[0], context)
        except AttributeError:
            pass
        result = compare_types(primary.primType, typeRef)
        LOG.debug(logmsg + 'YES' if result else 'NO')
        return result
    elif (actual_type.kind in ('IntegerType', 'RealType') and
            (primary.kind == 'numericalValue' or
                                   primary.primType.kind == actual_type.kind)):
        LOG.debug(logmsg + 'YES')
        return True
    elif actual_type.kind == 'BooleanType' and primary.kind == 'booleanValue':
        LOG.debug(logmsg + 'YES')
        return True
    elif (primary.kind == 'emptyString' and
                                         actual_type.kind == 'SequenceOfType'):
        if int(actual_type.Min) == 0:
            LOG.debug(logmsg + 'YES')
            return True
        else:
            LOG.debug(logmsg + 'NO (SEQUENCE OF has a minimum size of '
                             + actual_type.Min + ')')
            return False
    elif primary.kind == 'sequenceOf' and actual_type.kind == 'SequenceOfType':
        if (len(primary.sequenceOf) < int(actual_type.Min) or
                len(primary.sequenceOf) > int(actual_type.Max)):
            LOG.debug(logmsg + 'NO (' + len(primary.sequenceOf) +
                      'elems, while constraint is [' +
                      actual_type.Min + '..' + actual_type.Max, '])')
            return False
        for elem in primary.sequenceOf:
            if not isOfCompatibleType(elem, actual_type.type, context):
                LOG.debug(logmsg + 'NO')
                return False
        LOG.debug(logmsg + 'YES')
        return True
    elif primary.kind == 'sequence' and actual_type.kind == 'SequenceType':
        user_nb_elem = len(primary.sequence.keys())
        type_nb_elem = len(actual_type.Children.keys())
        if user_nb_elem != type_nb_elem:
            LOG.debug(logmsg + 'NO '
                      '(not the right number of fields in the sequence)')
            return False
        else:
            for field, fd_data in actual_type.Children.viewitems():
                ufield = field.replace('-', '_')
                if ufield not in primary.sequence:
                    LOG.debug(logmsg + 'NO (missing field ' + ufield + ')')
                    return False
                else:
                    # If the user field is a raw value
                    if primary.sequence[ufield].is_raw():
                        if not isOfCompatibleType(
                                primary.sequence[ufield].var, fd_data.type,
                                context):
                            LOG.debug(logmsg + 'NO (field ' + ufield +
                                      ' is not of the proper type, i.e. ' +
                                      type_name(fd_data.type) + ')')
                            return False
                    # Compare the types for semantic equivalence
                    elif not compare_types(
                        primary.sequence[ufield].exprType, fd_data.type):
                        LOG.debuglogmsg + ('NO (field ' + ufield +
                            ' is not of the proper type, i.e. ' +
                            type_name(fd_data.type) + ')')
                        return False
            LOG.debug(logmsg + 'YES')
            return True
    elif primary.kind == 'choiceItem' and actual_type.kind == 'ChoiceType':
        if primary.choiceItem['choice'] not in actual_type.Children.keys():
            LOG.debug(logmsg + 'NO (non-existent choice)')
            return False
        else:
            # compare primary.choiceItem['value']
            # with actual_type['Children'][primary.choiceItem['choice']]
            value = primary.choiceItem['value']
            typeOfChoiceField = \
                    actual_type.Children[primary.choiceItem['choice']].type
            # if the user field is a raw value:
            if value.is_raw():
                if not isOfCompatibleType(value.var, typeOfChoiceField,
                        context):
                    LOG.debug(logmsg + 'NO (field ' +
                              primary.choiceItem['choice'] +
                              ' is not of the proper type)')
                    return False
            # Compare the types for semantic equivalence:
            elif not compare_types(primary.choiceItem['value'].exprType,
                                   typeOfChoiceField):
                LOG.debug(logmsg + 'NO (field ' + primary.choiceItem['choice']
                                 + ' is not of the proper type)')
                return False
            if value.kind == 'primary':
                # Set the type of the choice field
                value.var.primType = typeOfChoiceField
        LOG.debug(logmsg + 'YES')
        return True
    elif primary.kind == 'stringLiteral':
        # Octet strings
        try:
            basic_type = find_basic_type(typeRef)
        except TypeError as err:
            LOG.error(str(err))
            LOG.debug(logmsg + 'NO')
            return False
        if(basic_type.kind.endswith('StringType') and
           int(basic_type.Min) <= len(
                          primary.stringLiteral[1:-1]) <= int(basic_type.Max)):
            LOG.debug(logmsg + 'YES: String literal is within bounds')
            return True
        else:
            LOG.debug(logmsg + 'NO (incompatible string literal)')
            return False
    elif primary.kind == 'ifThenElse':
        # check that IF expr returns BOOL, and that Then and Else expressions
        # are compatible with actual_type
        if_expr = primary.ifThenElse['if']
        then_expr = primary.ifThenElse['then']
        else_expr = primary.ifThenElse['else']
        if if_expr.exprType.kind != 'BooleanType':
            LOG.debug(logmsg + 'NO (IF expression does not return a boolean)')
            return False
        else:
            for expr in (then_expr, else_expr):
                if expr.is_raw():
                    if not isOfCompatibleType(expr.var, typeRef, context):
                        LOG.debug(logmsg + 'NO (' +
                                  expr.var.inputString +
                                  ' is not of the proper type)')
                        return False
                    else:
                        expr.var.primType = typeRef
                        expr.exprType = typeRef
                # compare the types for semantic equivalence:
                elif not compare_types(expr.exprType, typeRef):
                    LOG.debug(logmsg + 'NO (' + expr.inputString +
                              ' is not of the proper type)')
                    return False
        LOG.debug(logmsg + 'YES')
        return True
    elif (primary.kind == 'mantissaBaseExpFloat' and
        actual_type.kind == 'RealType'):
        LOG.debug(logmsg + 'PROBABLY (it is a float but I did not check'
                           'if values are compatible)')
        return True
    else:
        LOG.debug(logmsg + 'NO (Cannot conclude - assuming not)')
        return False


def compare_types(type_a, type_b):
    ''' Compare two types, return True if they are semantically equivalent '''
    # Build the set of References for each type and look for an intersection
    logmsg = '[compare_types]' + str(type_a) + ' and ' + str(type_b) + ': '
    if type_a == type_b:
        LOG.debug(logmsg + 'YES (1)')
        return True
    try:
        type_a = find_basic_type(type_a)
        type_b = find_basic_type(type_b)
    except TypeError as err:
        LOG.error(str(err))
        LOG.debug(logmsg + 'NO')
        return False
    # After reaching the lowest type description, check again for equality
    if type_a == type_b:
        LOG.debug(logmsg + 'YES (2)')
        return True
    # Check if both types have basic compatibility
    simple_types = [elem for elem in (type_a, type_b) if elem.kind in
                       ('IntegerType', 'BooleanType', 'RealType',
                        'SequenceOfType', 'StringType', 'OctetStringType')]
    if len(simple_types) < 2:
        # Either A or B is not a basic type - cannot be compatible
        LOG.debug(logmsg + 'NO (one is not a basic type)')
        return False
    elif type_a.kind == type_b.kind:
        if type_a.kind == 'SequenceOfType':
            if type_a.Min == type_b.Min and type_a.Max == type_b.Max:
                result = compare_types(type_a.type, type_b.type)
                LOG.debug(logmsg + 'YES' if result else 'NO')
                return result
            else:
                LOG.debug(logmsg + 'NO (incompatible arrays)')
                return False
        LOG.debug(logmsg + 'YES (3)')
        return True
    elif type_a.kind.endswith('StringType') and type_b.kind.endswith(
                                                                 'StringType'):
        # Allow Octet String values to be printable strings.. for convenience
        LOG.debug(logmsg + 'YES (4)')
        return True
    elif not(type_a.kind in ('IntegerType', 'RealType') and
             type_b.kind in ('IntegerType', 'RealType')):
        LOG.debug(logmsg + 'NO (Int/Real mismatch)')
        return False
    else:
        LOG.debug(logmsg + 'YES (5)')
        return True


def find_variable(var, context):
    ''' Look for a variable name in the context and return its type '''
    result = UNKNOWN_TYPE
    LOG.debug('[find_variable] checking if ' + str(var) + ' is defined')
    # all DCl-variables
    all_visible_variables = dict(context.variables)
    all_visible_variables.update(context.global_variables)
    # First check locally, i.e. in FPAR
    try:
        for variable in context.fpar:
            if variable['name'].lower() == var.lower():
                return variable['type']
    except AttributeError:
        # No FPAR section
        pass
    for varname, vartype in all_visible_variables.viewitems():
        # Case insensitive comparison with variables
        if var.lower() == varname.lower():
            result = vartype
            return result
    for timer in context.timers:
        if var.lower() == timer.lower():
            return result

    LOG.debug('[find_variable] result: not found, raising exception')
    raise AttributeError('Variable {var} not defined'.format(var=var))


def find_type(path, context):
    '''
        Determine the type of an element using the data model,
        and the list of variables, operators and procedures
    '''
    errors = []
    warnings = []
    result = UNKNOWN_TYPE
    if not DV:
        errors.append('Dataview is required to process types')
        return result, errors, warnings
    LOG.debug('[find_type] ' + str(path))
    if path:
        # First, find the type of the main element
        # (variable, operator/procedure return type)
        main = path[0]
        if unicode.isnumeric(main):
            result = type('', (object,),
                    {'kind': 'IntegerType', 'Min': main, 'Max': main})
        else:
            try:
                float(main)
                result = type('', (object,),
                        {'kind': 'RealType', 'Min': main, 'Max': main})
            except ValueError:
                v, o = None, None
                # Try to find the name in the variables list
                # Guard (len(path)>1) is used to skip the type
                # detection when the value is a single field.
                try:
                    if len(path) > 1:
                        result = find_variable(main, context)
                    else:
                        raise ValueError
                except (AttributeError, ValueError):
                    for o in context.operators.viewkeys():
                        # Case insensitive comparison with operators
                        if main.lower() == o.lower() and len(path) > 1:
                            result = new_ref_type(context.operators[o])
                            break
                    else:
                        if main.lower() in ('true', 'false'):
                            result = type('', (object,),
                                    {'kind': 'BooleanType'})
                        elif(main.lower() in SPECIAL_OPERATORS
                                and len(path) > 1):
                            # Special operators require type elaboration
                            if main.lower() == 'present':
                                result = type('', (object,),
                                              {'kind': 'ChoiceEnumeratedType',
                                               'EnumValues': {}})
                                # present(choiceType): must return an enum
                                # with elements being the choice options
                                param, = path[1].get('procParams') or [None]
                                if not param:
                                    errors.append('Missing parameter'
                                                  ' in PRESENT clause')
                                else:
                                    try:
                                        param_type = find_basic_type(
                                                                param.exprType)
                                    except TypeError as err:
                                        errors.append('[find_type]' + str(err))
                                    if param_type.kind != 'ChoiceType':
                                        errors.append('PRESENT parameter'
                                                ' must be a CHOICE type')
                                    else:
                                        result.EnumValues = param_type.Children
                            elif main.lower() in (
                                                 'write', 'writeln', 'length'):
                                result = type('', (object,),
                                              {'kind': 'IntegerType'})
                        else:
                            pass
    if result.kind == 'ReferenceType' and len(path) > 1:
        # We have more than one element and the first one is of type 'result'
        # Iterate over the path to get the type of the last element
        for elem in path[1:]:
            try:
                basic = find_basic_type(result)
            except TypeError as err:
                 errors.append(str(err))
                 return result, errors, warnings
            if 'procParams' in elem:
                # Discard operator parameters: they do not change the type
                continue
            # Sequence, Choice (case insensitive)
            if basic.kind in ('SequenceType', 'ChoiceType'):
                elem_asn1 = elem.replace('_', '-').lower()
                type_idx = [c for c in basic.Children
                            if c.lower() == elem_asn1]
                if type_idx:
                    result = basic.Children[type_idx[0]].type
                else:
                    errors.append('Field ' + elem + ' not found in expression '
                              + '!'.join(path))
                    result = UNKNOWN_TYPE
                    break
            # Sequence of
            elif basic.kind == 'SequenceOfType':
                # Can be an index or a substring
                if 'index' in elem:
                    # Index - change to the type of the Seqof elements
                    result = basic.type
                elif 'substring' in elem:
                    # Don't change the type, still a SEQUENCE OF
                    # XXX Size may differ
                    pass
            elif basic.kind == 'EnumeratedType':
                pass
            elif basic.kind.endswith('StringType'):
                # Can be an index or a substring
                if 'index' in elem:
                    errors.append('Index on a string is not supported')
                elif 'substring' in elem:
                    # don't change type, returns a string
                    # XXX Size may differ
                    pass
            else:
                errors.append('Expression ' + '!'.join(path) +
                              ' does not resolve - check field "' +
                              str(elem) + '"')
                result = UNKNOWN_TYPE
                break
    return result, errors, warnings


def expression_list(root, context):
    ''' Parse a list of expression parameters '''
    errors = []
    warnings = []
    result = []
    for param in root.getChildren():
        exp, err, warn = expression(param, context)
        errors.extend(err)
        warnings.extend(warn)
        result.append(exp)
    return result, errors, warnings

def primary_value(root, prim=None, context=None):
    '''
        Process a primary expression such as a!b(4)!c(hello)
        or { x 1, y a:2 } (ASN.1 Value Notation)
    '''
    warnings = []
    errors = []
    prim.kind = 'primaryId'
    first_id = ''
    global TMPVAR
    for child in root.getChildren():
        if child.type == lexer.ID:
            first_id = child.text
            prim.primaryId = [first_id]
        elif child.type == lexer.INT:
            prim.kind = 'numericalValue'
            prim.primaryId = [child.text.lower()]
        elif child.type in (lexer.TRUE, lexer.FALSE):
            prim.kind = 'booleanValue'
            prim.primaryId = [child.text.lower()]
        elif child.type == lexer.FLOAT:
            prim.kind = 'numericalValue'
            prim.primaryId = [child.getChild(0).text]
        elif child.type == lexer.STRING:
            prim.kind = 'stringLiteral'
            prim.stringLiteral = child.getChild(0).text
        elif child.type == lexer.FLOAT2:
            prim.kind = 'mantissaBaseExpFloat'
            mant = int(child.getChild(0).toString())
            base = int(child.getChild(1).toString())
            exp = int(child.getChild(2).toString())
            prim.mantissaBaseExpFloat = {'mantissa': mant,
                                         'base': base,
                                         'exponent': exp}
            prim.primType = type('',(object,), {'kind': 'RealType'})
        elif child.type == lexer.EMPTYSTR:
            # Empty SEQUENCE OF (i.e. "{}")
            prim.kind = 'emptyString'
        elif child.type == lexer.CHOICE:
            prim.kind = 'choiceItem'
            choice = child.getChild(0).toString()
            expr, err, warn = expression(child.getChild(1), context)
            errors.extend(err)
            warnings.extend(warn)
            prim.choiceItem = {'choice': choice, 'value': expr}
        elif child.type == lexer.SEQUENCE:
            prim.kind = 'sequence'
            for elem in child.getChildren():
                if elem.type == lexer.ID:
                    field_name = elem.text
                else:
                    prim.sequence[field_name], err, warn = (
                            expression(elem, context))
                    errors.extend(err)
                    warnings.extend(warn)
        elif child.type == lexer.SEQOF:
            prim.kind = 'sequenceOf'
            for elem in child.getChildren():
                prim_elem = ogAST.Primary(
                        get_input_string(elem), elem.getLine(),
                        elem.getCharPositionInLine())
                prim_elem, err, warn = primary_value(
                                          elem, prim_elem, context=context)
                errors.extend(err)
                warnings.extend(warn)
                prim.sequenceOf.append(prim_elem)
        elif child.type == lexer.BITSTR:
            prim.kind = 'bitString'
            warnings.append('Bit string literal not supported yet')
        elif child.type == lexer.OCTSTR:
            prim.kind = 'octetString'
            warnings.append('Octet string literal not supported yet')
        elif child.type == lexer.PARAMS:
            # Cover parameters of operator calls within a task
            # but not parameters of output or procedure calls
            if not first_id:
                errors.append(
                        'Ground expression cannot have index or params: ' +
                        get_input_string(root))
                return [], errors, warnings
            expr_list, err, warn = expression_list(child, context)
            errors.extend(err)
            warnings.extend(warn)
            procedures_list = [proc.inputString.lower() for proc in
                    context.procedures]
            if first_id.lower() in SPECIAL_OPERATORS + procedures_list:
                # here we must check/set the type of each param
                try:
                    check_and_fix_op_params(
                            first_id.lower(), expr_list, context)
                except (AttributeError, TypeError) as err:
                    errors.append(str(err) + '- ' + get_input_string(root))
                prim.primaryId.append({'procParams': expr_list})
            else:
                if len(expr_list) == 1:
                    # Index (only one param)
                    prim.primaryId.append({'index': expr_list})
                elif len(expr_list) == 2:
                    # Substring (range, two params)
                    prim.primaryId.append(
                            {'substring': expr_list, 'tmpVar': TMPVAR})
                    TMPVAR += 1
                else:
                    errors.append('Wrong number of parameters')
        elif child.type == lexer.FIELD_NAME:
            if not first_id:
                errors.append(
                        'Ground expression cannot have index or params: ' +
                        get_input_string(root))
                return [], errors, warnings
            prim.primaryId.append(child.getChild(0).text)
        else:
            warnings.append('Unsupported primary construct, type:' +
                    str(child.type) +
                    ' (line ' + str(child.getLine()) + ')')
    if prim.primaryId and not prim.primType:
        # Determine the type of a construct of the form a!b!c!d (path)
        prim.primType, err, warn = find_type(prim.primaryId, context)
        errors.extend(err)
        warnings.extend(warn)
    elif prim.kind == 'stringLiteral':
        # Preliminary support of string types (used at least in WRITE(LN))
        prim.primType = type('', (object,),
                             {'kind': 'StringType',
                              'Min': str(len(prim.stringLiteral)-2),
                              'Max': str(len(prim.stringLiteral)-2)})
    if is_constant(prim):
        prim.kind = 'constant'
    return prim, errors, warnings

def primary(root, context):
    ''' Process a primary (-/NOT value) '''
    warnings = []
    errors = []
    prim = ogAST.Primary(
            get_input_string(root),
            root.getLine(),
            root.getCharPositionInLine())
    for child in root.getChildren():
        if child.type == lexer.NOT:
            prim.op_not = True
        elif child.type == lexer.MINUS:
            prim.op_minus = True
        elif child.type == lexer.PRIMARY_ID:
            # Covers variable reference, indexed values,
            # and ASN.1 value notation
            prim, err, warn = primary_value(child, prim, context=context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.EXPRESSION:
            prim.kind = 'expression'
            prim.expr, err, warn = expression(child.getChild(0), context)
            errors.extend(err)
            warnings.extend(warn)
            prim.primType = prim.expr.exprType
        elif child.type == lexer.IFTHENELSE:
            prim.kind = 'ifThenElse'
            if_part, then_part, else_part = child.getChildren()
            if_expr, err, warn = expression(if_part, context)
            errors.extend(err)
            warnings.extend(warn)
            then_expr, err, warn = expression(then_part, context)
            errors.extend(err)
            warnings.extend(warn)
            else_expr, err, warn = expression(else_part, context)
            errors.extend(err)
            warnings.extend(warn)
            global TMPVAR
            prim.ifThenElse = {'if': if_expr,
                              'then': then_expr,
                              'else': else_expr,
                              'tmpVar': TMPVAR}
            prim.primType = UNKNOWN_TYPE
            TMPVAR += 1
        else:
            warnings.append('Unsupported primary child type:' +
                    str(child.type) + ' (line ' +
                    str(child.getLine()) + ')')
    return prim, errors, warnings

def expression(root, context):
    ''' Expression analysis (e.g. 5+5*hello(world)!foo) '''
    errors = []
    warnings = []
    global TMPVAR
    expr = ogAST.Expression(get_input_string(root), root.getLine(),
            root.getCharPositionInLine())
    expr.exprType = UNKNOWN_TYPE

    if root.type in (lexer.PLUS,
                     lexer.ASTERISK,
                     lexer.DASH,
                     lexer.APPEND,
                     lexer.IMPLIES,
                     lexer.OR,
                     lexer.XOR, 
                     lexer.AND,
                     lexer.EQ, 
                     lexer.NEQ, 
                     lexer.GT, 
                     lexer.GE, 
                     lexer.LT, 
                     lexer.LE, 
                     lexer.IN, 
                     lexer.DIV, 
                     lexer.MOD, 
                     lexer.REM):
        left, right = root.getChildren()

        if root.type == lexer.IN:
            # Left and right are reversed for IN operator
            left, right = right, left

        expr.left, err_left, warn_left = expression(left, context)
        expr.right, err_right, warn_right = expression(right, context)
        errors.extend(err_left)
        warnings.extend(warn_left)
        errors.extend(err_right)
        warnings.extend(warn_right)

        # If type of the left part of the expression is still unknown
        # then look in the list of DCL variables for it
        # left expr only must be resolved because right part could
        # be an enumerated, which value name could conflict with a
        # variable name. left part cannot be an enumerated name.
        if expr.left.exprType.kind == 'UnknownType':
            try:
                expr.left.exprType = find_variable(expr.left.inputString,
                                                   context)
            except AttributeError:
                pass
        # Get typenames
        left_typename, right_typename = [
                type_name(side.exprType) for side in (expr.left, expr.right)]

        # If only one of the operands is a raw value,
        # check for type compatibility with the other operand

        for side in (expr.right, expr.left):
            if side.is_raw():
                raw_expr = side
                if side.exprType.kind in ('IntegerType', 'RealType'):
                    side.var.kind = 'numericalValue'
            else:
                typed_expr = side

        # Presently no type check when using ASN.1-defined constants
        if is_constant(expr.right.var):
            expr.right.exprType = expr.left.exprType
        elif is_constant(expr.left.var):
            expr.left.exprType = expr.right.exprType

        if root.type == lexer.IN:
            # Check that left is a sequence of or a string
            container_basic_type = find_basic_type(expr.left.exprType)
            if container_basic_type.kind == 'SequenceOfType':
                ref_type = container_basic_type.type
            elif container_basic_type.kind.endswith('StringType'):
                ref_type = container_basic_type
            else:
                ref_type = None
                errors.append('IN expression: right part must be a list')
            if expr.right.is_raw() and ref_type and not isOfCompatibleType(
                                            expr.right.var, ref_type, context):
                errors.append('Incompatible raw type in IN expression')
            elif not expr.right.is_raw() and ref_type and not compare_types(
                                                ref_type, expr.right.exprType):
                errors.append('Incompatible types in IN expression')

        elif expr.right.is_raw() != expr.left.is_raw():
            # ^ This is an XOR ("Sherif de l'espace")
            if not isOfCompatibleType(
                    raw_expr.var, typed_expr.exprType, context):
                # Raw value not of the same type as the typed value
                # (But in lexer.IN case, it could still be OK, we must
                # compare against SEQOF internal type)
                errors.append('Incompatible types in expression: left (' +
                        expr.left.inputString + ', type = ' +
                        left_typename + '), right (' +
                        expr.right.inputString +
                        ', type = ' +
                        right_typename + ') (line ' +
                        str(expr.line) + ')')
            else:
                raw_expr.exprType = typed_expr.exprType
                # Propagate the type to the primary
                raw_expr.var.primType = typed_expr.exprType

        elif not compare_types(expr.left.exprType, expr.right.exprType):
            errors.append('Types are incompatible in expression: left (' +
                    expr.left.inputString + ', type= ' +
                    left_typename + '), right (' +
                    expr.right.inputString +
                    ', type= ' +
                    right_typename +
                    ') (line ' + str(expr.line) + ')')
    if root.type in (lexer.AND,
                     lexer.EQ,
                     lexer.NEQ,
                     lexer.GT,
                     lexer.GE,
                     lexer.LT,
                     lexer.LE,
                     lexer.OR,
                     lexer.XOR,
                     lexer.AND,
                     lexer.IN):
        expr.exprType = type('', (object,), {'kind': 'BooleanType'})
    elif root.type in (lexer.PLUS,
                       lexer.ASTERISK,
                       lexer.DASH,
                       lexer.APPEND,
                       lexer.REM,
                       lexer.MOD):
        expr.exprType = expr.left.exprType
    try:
        expr.kind = OPKIND[root.type]
    except:
        warnings.append('Unsupported expression construct, type: ' +
                str(root.type))
    if root.type == lexer.PRIMARY:
        expr.var, err, warn = primary(root, context)
        errors.extend(err)
        warnings.extend(warn)
        # Type of expression is the type of the primary
        # (if set - otherwise keep Unknown)
        if expr.var.primType:
            expr.exprType = expr.var.primType
    # Expressions may need intermediate storage for code generation
    expr.tmpVar = TMPVAR
    TMPVAR += 1
    return expr, errors, warnings

def variables(root, ta_ast, context):
    ''' Process declarations of variables (dcl a,b Type := 5) '''
    var = []
    errors = []
    warnings = []
    asn1_sort = UNKNOWN_TYPE
    for child in root.getChildren():
        if child.type == lexer.ID:
            var.append(child.text)
        elif child.type == lexer.SORT:
            sort = child.getChild(0).text
            # Find corresponding type in ASN.1 model
            try:
                asn1_sort = sdl_to_asn1(sort)
            except TypeError as err:
                errors.append(str(err) + '(line ' + str(child.getLine()) + ')')
        elif child.type == lexer.GROUND:
            pass
            # TODO Expression - make a default value assignment
            # expression(child)
        else:
            warnings.append('Unsupported variables construct type: ' +
                    str(child.type))
    for variable in var:
        # Add to the context and text area AST entries
        context.variables[variable] = asn1_sort
        ta_ast.variables[variable] = asn1_sort
    if not DV:
        errors.append('Cannot do semantic checks on variable declarations')
    return errors, warnings

def dcl(root, ta_ast, context):
    ''' Process a set of variable declarations '''
    errors = []
    warnings = []
    for child in root.getChildren():
        if child.type == lexer.VARIABLES:
            err, warn = variables(child, ta_ast, context)
            errors.extend(err)
            warnings.extend(warn)
        else:
            warnings.append(
                    'Unsupported dcl construct, type: ' + str(child.type))
    return errors, warnings

def fpar(root):
    ''' Process a formal parameter declaration '''
    errors = []
    warnings = []
    params = []
    asn1_sort = UNKNOWN_TYPE
    for param in root.getChildren():
        param_names = []
        sort = ''
        direction = 'in'
        assert(param.type == lexer.PARAM)
        for child in param.getChildren():
            if child.type == lexer.INOUT:
                direction = 'out'
            elif child.type == lexer.IN:
                pass
            elif child.type == lexer.ID:
                # variable name
                param_names.append(child.text)
            elif child.type == lexer.SORT:
                sort = child.getChild(0).text
                try:
                    asn1_sort = sdl_to_asn1(sort)
                except TypeError as err:
                    errors.append(str(err) +
                            '(line ' + str(child.getLine()) + ')')
                for name in param_names:
                    params.append({'name': name, 'direction': direction,
                                   'type': asn1_sort})
            else:
                warnings.append(
                        'Unsupported construct in FPAR, type: ' +
                        str(child.type))
    return params, errors, warnings

def procedure(root, parent=None, context=None):
    ''' Parse a procedure definition '''
    proc = ogAST.Procedure()
    # Create a list of all inherited data
    try:
        proc.global_variables = dict(context.variables)
        proc.global_variables.update(context.global_variables)
        proc.input_signals = context.input_signals
        proc.output_signals = context.output_signals
        proc.procedures = context.procedures
        proc.operators = dict(context.operators)
    except AttributeError:
        LOG.debug('Procedure context is undefined')
    # Gather the list of states defined in the procedure
    states = get_state_list(root)
    for statename in states:
        # map a list of transitions to each state
        proc.mapping[statename] = []
    errors = []
    warnings = []
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            proc.pos_x, proc.pos_y, proc.width, proc.height = cif(child)
        elif child.type == lexer.ID:
            proc.inputString = child.toString()
        elif child.type == lexer.TEXTAREA:
            textarea, err, warn = text_area(child, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.textAreas.append(textarea)
        elif child.type == lexer.PROCEDURE:
            new_proc, err, warn = procedure(child, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.inner_procedures.append(new_proc)
        elif child.type == lexer.EXTERNAL:
            proc.external = True
        elif child.type == lexer.FPAR:
            params, err, warn = fpar(child)
            errors.extend(err)
            warnings.extend(warn)
            proc.fpar = params
        elif child.type == lexer.START:
            # START transition (fills the mapping structure)
            proc.content.start, err, warn = start(child, context=proc)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.STATE:
            # STATE - fills up the 'mapping' structure.
            newstate, err, warn = state(child, parent=None, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.states.append(newstate)
        elif child.type == lexer.FLOATING_LABEL:
            lab, err, warn = floating_label(child, parent=None, context=proc)
            errors.extend(err)
            warnings.extend(warn)
            proc.content.floating_labels.append(lab)
        else:
            warnings.append(
                    'Unsupported construct in procedure, type: ' +
                    str(child.type))
    return proc, errors, warnings


def floating_label(root, parent, context):
    ''' Floating label: name and optional transition '''
    _ = parent
    errors = []
    warnings = []
    lab = ogAST.Floating_label()
    # Keep track of the number of terminator statements following the label
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.ID:
            lab.inputString = child.text
            lab.line = child.getLine()
            lab.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.CIF:
            # Get symbol coordinates
            lab.pos_x, lab.pos_y, lab.width, lab.height = cif(child)
        elif child.type == lexer.HYPERLINK:
            lab.hyperlink = child.getChild(0).text[1:-1]
        elif child.type == lexer.TRANSITION:
            trans, err, warn = transition(
                                    child, parent=lab, context=context)
            errors.extend(err)
            warnings.extend(warn)
            lab.transition = trans
        else:
            warnings.append(
                    'Unsupported construct in floating label: ' +
                    str(child.type))
    # At the end of the label parsing, get the the list of terminators that
    # the transition contains by making a diff with the list at context
    # level (we counted the number of terminators before parsing the item)
    lab.terminators = list(context.terminators[terminators:])
    return lab, errors, warnings


def text_area_content(root, ta_ast, context):
    ''' Content of a text area: DCL, operators, procedures  '''
    errors = []
    warnings = []
    for child in root.getChildren():
        if child.type == lexer.DCL:
            err, warn = dcl(child, ta_ast, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.PROCEDURE:
            proc, err, warn = procedure(child, context=context)
            errors.extend(err)
            warnings.extend(warn)
            # Add procedure to the container (process or procedure)
            context.content.inner_procedures.append(proc)
        elif child.type == lexer.FPAR:
            params, err, warn = fpar(child)
            errors.extend(err)
            warnings.extend(warn)
            try:
                if context.fpar:
                    errors.append('Duplicate declaration of FPAR section')
                else:
                    context.fpar = params
            except AttributeError:
                errors.append('Only procedures can have an FPAR section')
        elif child.type == lexer.TIMER:
            context.timers.extend(timer.text.lower()
                                            for timer in child.children)
        else:
            warnings.append(
                    'Unsupported construct in text area content, type: ' +
                    str(child.type))
    return errors, warnings

def text_area(root, parent=None, context=None):
    ''' Process a text area (DCL, procedure, operators declarations '''
    errors = []
    warnings = []
    ta = ogAST.TextArea()
    for child in root.getChildren():
        if child.type == lexer.CIF:
            userTextStartIndex = child.getTokenStopIndex() + 1
            ta.pos_x, ta.pos_y, ta.width, ta.height = cif(child)
        elif child.type == lexer.TEXTAREA_CONTENT:
            ta.line = child.getLine()
            ta.charPositionInLine = child.getCharPositionInLine()
            # Go update the process-level list of variables
            # (TODO: also ops and procedures)
            err, warn = text_area_content(child, ta, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.ENDTEXT:
            userTextStopIndex = child.getTokenStartIndex() - 1
            ta.inputString = token_stream(child).toString(
                    userTextStartIndex, userTextStopIndex).strip()
        elif child.type == lexer.HYPERLINK:
            ta.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported construct in text area, type: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    err = [[e, [ta.pos_x, ta.pos_y]] for e in errors]
    warn = [[w, [ta.pos_x, ta.pos_y]] for w in warnings]
    return ta, err, warn

def signal(root):
    ''' SIGNAL definition: name and optional list of types '''
    errors, warnings = [], []
    new_signal = {}
    for child in root.getChildren():
        if child.type == lexer.ID:
            new_signal['name'] = child.text
        elif child.type == lexer.PARAMNAMES:
            try:
                param_name, = [par.text for par in child.getChildren()]
                new_signal['param_name'] = param_name
            except ValueError:
                # Will be raised and reported at PARAMS token
                pass
        elif child.type == lexer.PARAMS:
            try:
                param, = [par.text for par in child.getChildren()]
                new_signal['type'] = sdl_to_asn1(param)
            except ValueError:
                errors.append(new_signal['name'] + ' cannot have more' +
                  ' than one parameter. Check signal declaration.')
    return new_signal, errors, warnings

def single_route(root):
    ''' Route (from id to id with [signal id] '''
    route = {'source': root.getChild(0).text,
             'dest': root.getChild(1).text,
             'signals': [sig.text for sig in root.getChildren()[2:]]}
    return route

def channel_signalroute(root):
    ''' Channel/signalroute definition (connections) '''
    # no AST entry for edges - a simple dict is sufficient
    # (name, [route])
    edge = {'routes': []}
    for child in root.getChildren():
        if child.type == lexer.ID:
            edge['name'] = child.text
        elif child.type == lexer.ROUTE:
            edge['routes'].append(single_route(child))
    return edge

def block_definition(root, parent):
    ''' BLOCK entity definition '''
    errors, warnings = [], []
    block = ogAST.Block()
    block.parent = parent
    parent.blocks.append(block)
    for child in root.getChildren():
        if child.type == lexer.ID:
            block.name = child.text
        elif child.type == lexer.SIGNAL:
            sig, err, warn = signal(child)
            errors.extend(err)
            warnings.extend(warn)
            block.signals.append(sig)
        elif child.type == lexer.CONNECTION:
            block.connections.append({'channel': cnx[0].text,
              'signalroute': cnx[1].text} for cnx in child.getChildren())
        elif child.type == lexer.BLOCK:
            block, err, warn = block_definition(child, parent=block)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.PROCESS:
            proc, err, warn = process_definition(child, parent=block)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.SIGNALROUTE:
            sigroute = channel_signalroute(child)
            block.signalroutes.append(sigroute)
        else:
            warnings.append('Unsupported block child type: ' +
                str(child.type))
    return block, errors, warnings

def system_definition(root, parent):
    ''' SYSTEM part - contains blocks, procedures and channels '''
    errors, warnings = [], []
    system = ogAST.System()
    # Store the name of the file where the system is defined
    system.filename = node_filename(root)
    system.ast = parent
    for child in root.getChildren():
        if child.type == lexer.ID:
            system.name = child.text
            LOG.debug('System name: ' + system.name)
        elif child.type == lexer.SIGNAL:
            sig, err, warn = signal(child)
            errors.extend(err)
            warnings.extend(warn)
            system.signals.append(sig)
            LOG.debug('Found signal: ' + str(sig))
        elif child.type == lexer.PROCEDURE:
            LOG.debug('procedure declaration')
            proc, err, warn = procedure(
                    child, parent=None, context=system)
            errors.extend(err)
            warnings.extend(warn)
            system.procedures.append(proc)
            LOG.debug('Added procedure: ' + proc.inputString)
        elif child.type == lexer.CHANNEL:
            LOG.debug('channel declaration')
            channel = channel_signalroute(child)
            system.channels.append(channel)
        elif child.type == lexer.BLOCK:
            LOG.debug('block declaration')
            block, err, warn = block_definition(child, parent=system)
            errors.extend(err)
            warnings.extend(warn)
        else:
            warnings.append('Unsupported construct in system: ' +
                    str(child.type))
    return system, errors, warnings

def pr_file(root):
    ''' Complete PR model - can be made up from several files/strings '''
    errors = []
    warnings = []
    ast = ogAST.AST()
    # Re-order the children of the AST to make sure system and use clauses
    # are parsed before process definition - to get signal definitions
    # and data typess references.
    processes, uses, systems = [], [], []
    for child in root.getChildren():
        ast.pr_files.add(node_filename(child))
        if child.type == lexer.PROCESS:
            processes.append(child)
        elif child.type == lexer.USE:
            uses.append(child)
        elif child.type == lexer.SYSTEM:
            systems.append(child)
        else:
            LOG.error('Unsupported construct in PR:' + str(child.type))
    for child in uses:
        LOG.debug('USE clause')
        # USE clauses can contain a CIF comment with the ASN.1 filename
        use_clause_subs = child.getChildren()
        for clause in use_clause_subs:
            if clause.type == lexer.ASN1:
                asn1_filename = clause.getChild(0).text[1:-1]
                ast.asn1_filenames.append(asn1_filename)
            else:
                ast.use_clauses.append(clause.text)
        try:
            global DV
            if not DV:
                # Here XXX call asn1.exe to create DataView.py
                # (Currently done in buildsupport)
                DV = importlib.import_module('DataView')
            else:
                reload(DV)
            ast.dataview = types()
            ast.asn1Modules = DV.asn1Modules
            # Add constants defined in the ASN.1 modules (for visibility)
            for mod in ast.asn1Modules:
                ast.asn1_constants.extend(DV.exportedVariables[mod])
        except (ImportError, NameError):
            LOG.info('USE Clause did not contain ASN.1 filename')
    for child in systems:
        LOG.debug('found SYSTEM')
        system, err, warn = system_definition(child, parent=ast)
        errors.extend(err)
        warnings.extend(warn)
        ast.systems.append(system)
        def find_processes(block):
            ''' Recursively find processes in a system '''
            try:
                result = [proc for proc in block.processes 
                          if not proc.referenced]
            except AttributeError:
                result = []
            for nested in block.blocks:
                result.extend(find_processes(nested))
            return result
        ast.processes.extend(find_processes(system))
    for child in processes:
        # process definition at root level (must be referenced in a system)
        LOG.debug('found PROCESS')
        process, err, warn = process_definition(child, parent=ast)
        process.dataview = ast.dataview
        process.asn1Modules = ast.asn1Modules
        errors.extend(err)
        warnings.extend(warn)
        #ast.processes.append(process)
    LOG.debug('all files: ' + str(ast.pr_files))
    return ast, errors, warnings

def process_definition(root, parent=None):
    ''' Process definition analysis '''
    errors = []
    warnings = []
    process = ogAST.Process()
    process.filename = node_filename(root)
    process.parent = parent
    parent.processes.append(process)
    # Prepare the transition/state mapping
    for state_id in get_state_list(root):
        process.mapping[state_id] = []
    for child in root.getChildren():
        if child.type == lexer.ID:
            # Get process (taste function) name
            process.processName = child.text
            try:
                # Retrieve process interface (PI/RI)
                async_signals, procedures = get_interfaces(
                        parent, child.text)
                process.input_signals.extend([sig for sig in async_signals
                    if sig['direction'] == 'in'])
                process.output_signals.extend([sig for sig in async_signals
                    if sig['direction'] == 'out'])
                process.procedures.extend(procedures)
            except AttributeError as err:
                LOG.error('Discarding process ' + child.text + ' ' + str(err))
            except TypeError as error:
                LOG.debug(str(error))
                errors.append(str(error))
        elif child.type == lexer.TEXTAREA:
            # Text zone where variables and operators are declared
            textarea, err, warn = text_area(child, context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.content.textAreas.append(textarea)
        elif child.type == lexer.START:
            # START transition (fills the mapping structure)
            process.content.start, err, warn = start(
                                             child, context=process)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.STATE:
            # STATE - fills up the 'mapping' structure.
            statedef, err, warn = state(
                    child, parent=None, context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.content.states.append(statedef)
        elif child.type == lexer.NUMBER_OF_INSTANCES:
            # Number of instances - discarded (working on a single process)
            pass
        elif child.type == lexer.PROCEDURE:
            proc, err, warn = procedure(
                    child, parent=None, context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.content.inner_procedures.append(proc)
        elif child.type == lexer.FLOATING_LABEL:
            lab, err, warn = floating_label(
                    child, parent=None, context=process)
            errors.extend(err)
            warnings.extend(warn)
            process.content.floating_labels.append(lab)
        elif child.type == lexer.REFERENCED:
            process.referenced = True
        else:
            warnings.append('Unsupported process definition child type: ' +
                    str(child.type))
    return process, errors, warnings

def input_part(root, parent, context):
    ''' Parse an INPUT - set of TASTE provided interfaces '''
    i = ogAST.Input()
    warnings = []
    errors = []
    # Keep track of the number of terminator statements follow the input
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            i.pos_x, i.pos_y, i.width, i.height = cif(child)
        elif child.type == lexer.INPUTLIST:
            i.inputString = get_input_string(child)
            i.line = child.getLine()
            i.charPositionInLine = child.getCharPositionInLine()
            # get input name and parameters (support for one parameter only)
            sig_param_type, user_param_type = None, None
            inputnames = [c for c in child.getChildren()
                                                  if c.type != lexer.PARAMS]
            for inputname in inputnames:
                for inp_sig in context.input_signals:
                    if inp_sig['name'].lower() == inputname.text.lower():
                        i.inputlist.append(inp_sig['name'])
                        sig_param_type = inp_sig.get('type')
                        break
                else:
                    for timer in context.timers:
                        if timer.lower() == inputname.text.lower():
                            i.inputlist.append(timer.lower())
                            break
                    else:
                        errors.append('Input signal or timer not declared: '
                            + inputname.toString() +
                            ' (line ' + str(i.line) + ')')
            if len(inputnames) > 1 and sig_param_type is not None:
                errors.append('Inputs in a list shall not expect parameters')
            # Parse all parameters (then check that there is only one)
            inputparams = [c.getChildren() for c in child.getChildren()
                                                     if c.type == lexer.PARAMS]
            if len(inputparams) > 1:
                # user entered e.g. INPUT a(x), b(y) instead of INPUT a,b
                errors.append('Only one input can have a parameter')
            elif len(inputparams) == 1 and sig_param_type is not None and \
                    len(inputparams[0]) == 1:
                user_param, = inputparams[0]
                try:
                    user_param_type = find_variable(user_param.text, context)
                    if not compare_types(sig_param_type, user_param_type):
                        errors.append('Parameter type does not match with '
                                      'signal declaration (expecting '
                                      'a variable of type ' +
                                      sig_param_type.ReferencedTypeName + ')')
                    else:
                        # Store parameter only if everything is OK
                        i.parameters = [user_param.text.lower()]
                except AttributeError as err:
                    errors.append(str(err))
            elif inputparams or sig_param_type:
                errors.append('Wrong number of parameters or type mismatch')

            # Report errors with symbol coordinates
            errors = [[e, [i.pos_x, i.pos_y]] for e in errors]
            warnings = [[w, [i.pos_x, i.pos_y]] for w in warnings]
        elif child.type == lexer.ASTERISK:
            # Asterisk means: all inputs not processed explicitely
            # Here we do not set the input list - it is set after
            # all other inputs are processed (see state function)
            i.inputString = get_input_string(child)
            i.line = child.getLine()
            i.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.PROVIDED:
            warnings.append('"PROVIDED" expressions not supported')
            i.provided = 'Provided'
        elif child.type == lexer.TRANSITION:
            trans, err, warn = transition(
                                    child, parent=i, context=context)
            errors.extend(err)
            warnings.extend(warn)
            i.transition = trans
            # Associate a reference to the transition to the list of inputs
            # The reference is an index to process.transitions table
            context.transitions.append(trans)
            i.transition_id = len(context.transitions) - 1
        elif child.type == lexer.COMMENT:
            i.comment, _, ___ = end(child)
        elif child.type == lexer.HYPERLINK:
            i.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported INPUT child type: ' +
                    str(child.type))
    # At the end of the input parsing, get the the list of terminators that
    # follow the input transition by making a diff with the list at process
    # level (we counted the number of terminators before parsing the input)
    i.terminators = list(context.terminators[terminators:])
    return i, errors, warnings

def state(root, parent, context):
    '''
        Parse a STATE.
        "parent" is used to compute absolute coordinates
        "context" is the AST used to store global data (process/procedure)
    '''
    errors = []
    warnings = []
    state_def = ogAST.State()
    asterisk_input = None
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            (state_def.pos_x, state_def.pos_y,
            state_def.width, state_def.height) = cif(child)
        elif child.type == lexer.STATELIST:
            # State name(state_def)
            state_def.inputString = get_input_string(child)
            state_def.line = child.getLine()
            state_def.charPositionInLine = child.getCharPositionInLine()
            for statename in child.getChildren():
                state_def.statelist.append(statename.toString())
        elif child.type == lexer.ASTERISK:
            state_def.inputString = get_input_string(child)
            state_def.line = child.getLine()
            state_def.charPositionInLine = child.getCharPositionInLine()
            exceptions = [c.toString() for c in child.getChildren()]
            for st in context.mapping:
                if st not in (exceptions, 'START'):
                    state_def.statelist.append(st)
        elif child.type == lexer.INPUT:
            # A transition triggered by an INPUT
            inp, err, warn = input_part(
                                     child, parent=state_def, context=context)
            errors.extend(err)
            warnings.extend(warn)
            try:
                for statename in state_def.statelist:
                    context.mapping[statename.lower()].append(inp)
            except KeyError:
                warnings.append('State definition missing')
            state_def.inputs.append(inp)
            if inp.inputString.strip() == '*':
                if asterisk_input:
                    errors.append('Multiple asterisk inputs under state ' +
                            str(state_def.inputString))
                else:
                    asterisk_input = inp
        elif child.type == lexer.COMMENT:
            state_def.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            state_def.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported STATE definition child type: ' +
                str(child.type))
    # post-processing: if state is followed by an ASTERISK input, the exact
    # list of inputs can be updated. Possible only if context has signals
    if context.input_signals and asterisk_input:
        explicit_inputs = set()
        for inp in state_def.inputs:
            explicit_inputs |= set(inp.inputlist)
        # Keep only inputs that are not explicitely defined
        input_signals = (sig['name'] for sig in context.input_signals)
        remaining_inputs = set(input_signals) - explicit_inputs
        asterisk_input.inputlist = list(remaining_inputs)

    return state_def, errors, warnings

def cif(root):
    ''' Return the CIF coordinates '''
    result = []
    for child in root.getChildren():
        if child.type == lexer.DASH:
            val = -int(child.getChild(0).toString())
        else:
            val = int(child.toString())
        result.append(val)
    return result

def start(root, parent=None, context=None):
    ''' Parse the START transition '''
    errors = []
    warnings = []
    if isinstance(context, ogAST.Procedure):
        s = ogAST.Procedure_start()
    else:
        s = ogAST.Start()
    # Keep track of the number of terminator statements following the start
    # useful if we want to render graphs from the SDL model
    terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            s.pos_x, s.pos_y, s.width, s.height = cif(child)
        elif child.type == lexer.TRANSITION:
            s.transition, err, warn = transition(
                                        child, parent=s, context=context)
            errors.extend(err)
            warnings.extend(warn)
            context.transitions.append(s.transition)
            context.mapping['START'] = len(
                                      context.transitions) - 1
        elif child.type == lexer.COMMENT:
            s.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            s.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('START unsupported child type: ' +
                    str(child.type))
    # At the end of the START parsing, get the the list of terminators that
    # follow the START transition by making a diff with the list at process
    # level (we counted the number of terminators before parsing the START)
    s.terminators = list(context.terminators[terminators:])
    return s, errors, warnings

def end(root, parent=None, context=None):
    ''' Parse a comment symbol '''
    c = ogAST.Comment()
    c.line = root.getLine()
    c.charPositionInLine = root.getCharPositionInLine()
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            c.pos_x, c.pos_y, c.width, c.height = cif(child)
        elif child.type == lexer.StringLiteral:
            c.inputString = child.toString()[1:-1]
        elif child.type == lexer.HYPERLINK:
            c.hyperlink = child.getChild(0).toString()[1:-1]
    return c, [], []


def procedure_call(root, parent, context):
    ''' Parse a PROCEDURE CALL (synchronous required interface) '''
    # Same as OUTPUT for external procedures
    o, err, warn = output(root, parent, context)
    o.kind = 'procedure_call'
    return o, err, warn


def outputbody(root, context):
    ''' Parse an output body (the content excluding the CIF statement) '''
    errors = []
    warnings = []
    body = {}
    for child in root.getChildren():
        if child.type == lexer.ID:
            body['outputName'] = child.text
            if child.text.lower() not in valid_output(context):
                errors.append('"' + child.text +
                              '" is not defined in the current scope')
        elif child.type == lexer.PARAMS:
            body['params'], err, warn = expression_list(
                                                    child, context)
            # here we must check/set the type of each param
            try:
                check_and_fix_op_params(
                    body.get('outputName') or '',
                    body['params'],
                    context)
            except (AttributeError, TypeError) as op_err:
                errors.append('[output] ' + str(op_err)
                              + ' - ' + get_input_string(root))
                LOG.debug('[outputbody] call check_and_fix_op_params : '
                            + get_input_string(root) + str(op_err))
                import traceback
                LOG.debug(str(traceback.format_exc()))
            errors.extend(err)
            warnings.extend(warn)
        else:
            warnings.append('Unsupported output body type:' +
                    str(child.type))
    if body.get('params'):
        body['tmpVars'] = []
        global TMPVAR
        for _ in range(len(body['params'])):
            body['tmpVars'].append(TMPVAR)
            TMPVAR += 1
    return body, errors, warnings


def output(root, parent, context):
    ''' Parse an OUTPUT :  set of asynchronous required interface(s) '''
    errors = []
    warnings = []
    o = ogAST.Output()
    o.kind = 'output'
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            o.pos_x, o.pos_y, o.width, o.height = cif(child)
        elif child.type == lexer.OUTPUT_BODY:
            o.inputString = get_input_string(child)
            o.line = child.getLine()
            o.charPositionInLine = child.getCharPositionInLine()
            body, err, warn = outputbody(child, context)
            errors.extend(err)
            warnings.extend(warn)
            o.output.append(body)
        elif child.type == lexer.COMMENT:
            o.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            o.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported output child type: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    err = [[e, [o.pos_x, o.pos_y]] for e in errors]
    warn = [[w, [o.pos_x, o.pos_y]] for w in warnings]
    return o, err, warn


def alternative_part(root, parent, context):
    ''' Parse a decision answer '''
    errors = []
    warnings = []
    ans = ogAST.Answer()
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            ans.pos_x, ans.pos_y, ans.width, ans.height = cif(child)
        elif child.type == lexer.CLOSED_RANGE:
            ans.kind = 'closed_range'
            ans.closedRange = [float(child.getChild(0).toString()),
                              float(child.getChild(1).toString())]
        elif child.type == lexer.CONSTANT:
            ans.kind = 'constant'
            ans.constant, err, warn = expression(
                                        child.getChild(0), context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.OPEN_RANGE:
            ans.kind = 'open_range'
            for c in child.getChildren():
                if c.type == lexer.CONSTANT:
                    ans.constant, err, warn = expression(
                            c.getChild(0), context)
                    errors.extend(err)
                    warnings.extend(warn)
                else:
                    ans.openRangeOp = OPKIND[c.type]
        elif child.type == lexer.INFORMAL_TEXT:
            ans.kind = 'informal_text'
            ans.informalText = child.getChild(0).toString()[1:-1]
        elif child.type == lexer.TRANSITION:
            ans.transition, err, warn = transition(
                                        child, parent=ans, context=context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.HYPERLINK:
            ans.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported answer type: ' + str(child.type))
        if child.type in (lexer.CLOSED_RANGE, lexer.CONSTANT,
                lexer.OPEN_RANGE, lexer.INFORMAL_TEXT):
            ans.inputString = get_input_string(child)
            ans.line = child.getLine()
            ans.charPositionInLine = child.getCharPositionInLine()
            # Report errors with symbol coordinates
            errors = [[e, [ans.pos_x, ans.pos_y]] for e in errors]
            warnings = [[w, [ans.pos_x, ans.pos_y]] for w in warnings]
    return ans, errors, warnings


def decision(root, parent, context):
    ''' Parse a DECISION '''
    errors = []
    warnings = []
    dec = ogAST.Decision()
    global TMPVAR
    dec.tmpVar = TMPVAR
    TMPVAR += 1
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            dec.pos_x, dec.pos_y, dec.width, dec.height = cif(child)
        elif child.type == lexer.QUESTION:
            dec.kind = 'question'
            decisionExpr, err, warn = expression(
                                        child.getChild(0), context)
            for e in err:
                errors.append([e, [dec.pos_x, dec.pos_y]])
            for w in warn:
                warnings.append([w, [dec.pos_x, dec.pos_y]])
            dec.question = decisionExpr
            dec.inputString = dec.question.inputString
            dec.line = dec.question.line
            dec.charPositionInLine = dec.question.charPositionInLine
            if dec.question.exprType.kind == 'UnknownType':
                try:
                    dec.question.exprType = find_variable(
                                     dec.question.inputString, context)
                except AttributeError:
                    pass
        elif child.type == lexer.INFORMAL_TEXT:
            dec.kind = 'informal_text'
            dec.inputString = get_input_string(child)
            dec.informalText = child.getChild(0).toString()[1:-1]
            dec.line = child.getLine()
            dec.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.ANY:
            dec.kind = 'any'
        elif child.type == lexer.COMMENT:
            dec.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            dec.hyperlink = child.getChild(0).toString()[1:-1]
        elif child.type == lexer.ANSWER:
            ans, err, warn = alternative_part(child, parent, context)
            errors.extend(err)
            warnings.extend(warn)
            dec.answers.append(ans)
            # Check that expression and answer types are compatible
            # TODO To be completed: constant that are not enum/int/bool
            # are not checked for existence)
            if ans.kind in ('constant', 'open_range'):
                if ans.constant.is_raw():
                    if not isOfCompatibleType(ans.constant.var,
                                        dec.question.exprType, context):
                        errors.append(ans.inputString +
                                ' is not type-compatible with ' +
                                dec.question.inputString)
                    else:
                        # Propagate Question type to answer constant
                        ans.constant.var.primType = dec.question.exprType
                        LOG.debug('ANSWER Kind: ' + str(ans.constant.var.kind))
                elif not compare_types(ans.constant.exprType,
                                                 dec.question.exprType):
                    errors.append(ans.inputString +
                            ' is not of a type compatible with ' +
                            dec.question.inputString)
            else:
                pass  # TODO: closed-range
        elif child.type == lexer.ELSE:
            dec.kind = child.toString()
            a = ogAST.Answer()
            a.inputString = 'ELSE'
            for c in child.getChildren():
                if c.type == lexer.CIF:
                    a.pos_x, a.pos_y, a.width, a.height = cif(c)
                elif c.type == lexer.TRANSITION:
                    a.transition, err, warn = transition(
                                            c, parent=a, context=context)
                    for e in err:
                        errors.append([e, [a.pos_x, a.pos_y]])
                    for w in warn:
                        warnings.append([w, [a.pos_x, a.pos_y]])
                elif child.type == lexer.HYPERLINK:
                    a.hyperlink = child.getChild(0).toString()[1:-1]
            a.kind = 'else'
            dec.answers.append(a)
        else:
            warnings.append(['Unsupported DECISION child type: ' +
                str(child.type), [dec.pos_x, dec.pos_y]])
    return dec, errors, warnings


def terminator_statement(root, parent, context):
    ''' Parse a terminator (NEXTSTATE, JOIN, STOP) '''
    errors = []
    warnings = []
    t = ogAST.Terminator()
    for term in root.getChildren():
        if term.type == lexer.CIF:
            t.pos_x, t.pos_y, t.width, t.height = cif(term)
        elif term.type == lexer.LABEL:
            lab, err, warn = label(term, parent=parent)
            errors.extend(err)
            warnings.extend(warn)
            t.label = lab
            context.labels.append(lab)
            lab.terminators = [t]
        elif term.type == lexer.NEXTSTATE:
            t.kind = 'next_state'
            t.inputString = term.getChild(0).toString()
            t.line = term.getChild(0).getLine()
            t.charPositionInLine = term.getChild(0).getCharPositionInLine()
            # Add next state infos at process level
            # Used in rendering backends to merge a NEXTSTATE with a STATE
            context.terminators.append(t)
        elif term.type == lexer.JOIN:
            t.kind = 'join'
            t.inputString = term.getChild(0).toString()
            t.line = term.getChild(0).getLine()
            t.charPositionInLine = term.getChild(0).getCharPositionInLine()
            context.terminators.append(t)
        elif term.type == lexer.STOP:
            t.kind = 'stop'
            context.terminators.append(t)
        elif term.type == lexer.COMMENT:
            t.comment, _, _ = end(term)
        elif term.type == lexer.HYPERLINK:
            t.hyperlink = term.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported terminator type: ' +
                    str(term.type))
    # Report errors with symbol coordinates
    err = [[e, [t.pos_x, t.pos_y]] for e in errors]
    warn = [[w, [t.pos_x, t.pos_y]] for w in warnings]
    return t, err, warn


def transition(root, parent, context):
    ''' Parse a transition '''
    errors = []
    warnings = []
    trans = ogAST.Transition()
    # Used to list terminators in this transition
    terminators = {'trans': len(context.terminators)}
    #terminators = len(context.terminators)
    for child in root.getChildren():
        if child.type == lexer.PROCEDURE_CALL:
            proc_call, err, warn = procedure_call(
                            child, parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(proc_call)
            parent = proc_call
        elif child.type == lexer.LABEL:
            term_count = len(context.terminators)
            lab, err, warn = label(child, parent=parent)
            terminators[lab] = term_count
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(lab)
            parent = lab
            context.labels.append(lab)
        elif child.type == lexer.TASK:
            tas, err, warn = task(
                            child, parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(tas)
            parent = tas
        elif child.type == lexer.OUTPUT:
            outp, err, warn = output(
                            child, parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(outp)
            parent = outp
        elif child.type == lexer.DECISION:
            dec, err, warn = decision(
                            child, parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.actions.append(dec)
            parent = dec
        elif child.type == lexer.TERMINATOR:
            term, err, warn = terminator_statement(child,
                    parent=parent, context=context)
            errors.extend(err)
            warnings.extend(warn)
            trans.terminator = term
        else:
            warnings.append('Unsupported symbol in transition, type: ' +
                    str(child.type))
    # At the end of the transition parsing, get the the list of terminators
    # the transition contains by making a diff with the list at context
    # level (we counted the number of terminators before parsing the item)
    trans.terminators = list(context.terminators[terminators.pop('trans'):])
    # Also update the list of terminators of each label in the transition
    for lab, term_count in terminators.viewitems():
        lab.terminators = list(context.terminators[term_count:])
    return trans, errors, warnings


def assign(root, context):
    ''' Parse an assignation (a := b) in a task symbol '''
    errors = []
    warnings = []
    expr = ogAST.Expression(
            get_input_string(root), root.getLine(),
            root.getCharPositionInLine())
    expr.kind = 'assign'
    for child in root.getChildren():
        if child.type == lexer.VARIABLE:
            # Left part of the assignation
            prim = ogAST.Primary(get_input_string(child), child.getLine(),
                    child.getCharPositionInLine())
            prim, err, warn = primary_value(child, prim, context)
            warnings.extend(warn)
            errors.extend(err)
            expr.left = ogAST.Expression(
                            get_input_string(child), child.getLine(),
                            child.getCharPositionInLine())
            expr.left.kind = 'primary'
            expr.left.var = prim
            expr.left.exprType = expr.left.var.primType
        else:
            # Right part of the assignation
            expr.right, err, warn = expression(child, context)
            errors.extend(err)
            warnings.extend(warn)
    if expr.left.exprType.kind == 'UnknownType':
        # Try to find the variable in the DCL list:
        try:
            expr.left.exprType = find_variable(expr.left.var.primaryId[0],
                                               context)
        except AttributeError:
            errors.append('Variable ' + expr.left.inputString +
                          ' is undefined (line '
                          + str(root.getLine()) + ', position ' +
                          str(root.getCharPositionInLine()) + ')')
            return expr, errors, warnings
    expr.left.var.primType = expr.left.exprType


    # If the right part is a value (not an identifier),
    # check if the value is compatible with the type
    if expr.right.is_raw() or is_constant(expr.right.var):
        if isOfCompatibleType(expr.right.var, expr.left.exprType, context):
            expr.right.exprType = expr.left.exprType
        else:
            errors.append(expr.right.inputString +
                    ' does not have a type compatible with ' +
                    expr.left.inputString)
            return expr, errors, warnings
    # Compare the types for semantic equivalence
    if not compare_types(expr.left.exprType, expr.right.exprType):
        errors.append(expr.right.inputString +
                ' has a type that is incompatible with ' +
                expr.left.inputString)
    else:
        if expr.right.kind == 'primary':
            # Propagate the type of the right expression
            # to its inner primary
            expr.right.var.primType = expr.left.var.primType
    return expr, errors, warnings


def task_body(root, t, context):
    ''' Parse the body of a task (excluding CIF and TASK tokens) '''
    errors = []
    warnings = []
    for child in root.getChildren():
        if child.type == lexer.ASSIGN:
            assig, err, warn = assign(child, context)
            errors.extend(err)
            warnings.extend(warn)
            t.kind = 'assign'
            t.assign.append(assig)
        elif child.type == lexer.INFORMAL_TEXT:
            t.kind = 'informal_text'
            t.informalText.append(child.getChild(0).toString()[1:-1])
        else:
            warnings.append('Unsupported child type in task body: ' +
                    str(child.type))
    return t, errors, warnings


def task(root, parent=None, context=None):
    ''' Parse a TASK symbol (assignation or informal text) '''
    errors = []
    warnings = []
    t = ogAST.Task()
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            t.pos_x, t.pos_y, t.width, t.height = cif(child)
        elif child.type == lexer.TASK_BODY:
            t.inputString = get_input_string(child)
            t.line = child.getLine()
            t.charPositionInLine = child.getCharPositionInLine()
            t, err, warn = task_body(child, t, context)
            errors.extend(err)
            warnings.extend(warn)
        elif child.type == lexer.COMMENT:
            t.comment, _, _ = end(child)
        elif child.type == lexer.HYPERLINK:
            t.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append('Unsupported child type in task definition: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    err = [[e, [t.pos_x, t.pos_y]] for e in errors]
    warn = [[w, [t.pos_x, t.pos_y]] for w in warnings]
    return t, err, warn


def label(root, parent, context=None):
    ''' Parse a LABEL symbol '''
    errors = []
    warnings = []
    lab = ogAST.Label()
    for child in root.getChildren():
        if child.type == lexer.CIF:
            # Get symbol coordinates
            lab.pos_x, lab.pos_y, lab.width, lab.height = cif(child)
        elif child.type == lexer.ID:
            lab.inputString = get_input_string(child)
            lab.line = child.getLine()
            lab.charPositionInLine = child.getCharPositionInLine()
        elif child.type == lexer.HYPERLINK:
            lab.hyperlink = child.getChild(0).toString()[1:-1]
        else:
            warnings.append(
                    'Unsupported child type in label definition: ' +
                    str(child.type))
    # Report errors with symbol coordinates
    err = [[e, [lab.pos_x, lab.pos_y]] for e in errors]
    warn = [[w, [lab.pos_x, lab.pos_y]] for w in warnings]
    return lab, err, warn


def add_to_ast(ast, filename=None, string=None):
    ''' Parse a file or string and add it to an AST '''
    errors, warnings = [], []
    try:
        parser = parser_init(filename=filename, string=string)
    except IOError:
        LOG.error('parser_init failed')
        raise
    # Use Sam & Max output capturer to get errors from ANTLR parser
    with samnmax.capture_ouput() as (stdout, stderr):
        tree_rule_return_scope = parser.pr_file()
    for e in stderr:
        errors.append([e.strip()])
    for w in stdout:
        warnings.append([w.strip()])
    # Root of the AST is of type antlr3.tree.CommonTree
    # Add it as a child of the common tree
    subtree = tree_rule_return_scope.tree
    token_stream = parser.getTokenStream()
    children_before = set(ast.children)
    # addChild does not simply add the subtree - it flattens it if necessary
    # this means that possibly SEVERAL subtrees can be added. We must set
    # the token_stream reference to all of them.
    ast.addChild(subtree)
    for tree in set(ast.children) - children_before:
        tree.token_stream = token_stream
    return errors, warnings


def parse_pr(files=None, string=None):
    ''' Parse SDL files (.pr) and/or string '''
    warnings = []
    errors = []
    files = files or []
    # define a common tree to combine several PR inputs
    common_tree = antlr3.tree.CommonTree(None)
    for filename in files:
        sys.path.insert(0, os.path.dirname(filename))
    for filename in files:
        err, warn = add_to_ast(common_tree, filename=filename)
    if string:
        err, warn = add_to_ast(common_tree, string=string)

    errors.extend(err)
    warnings.extend(warn)

    # At the end when common tree is complete, perform the parsing
    #for child in common_tree.children:
    og_ast, err, warn = pr_file(common_tree)
    for error in err:
        errors.append([error] if type(error) is not list else error)
    for warning in warn:
        warnings.append([warning] if type(warning) is not list else warning)
    # Post-parsing: additional semantic checks
    # check that all NEXTSTATEs have a correspondingly defined STATE
    # (except the '-' state, which means "stay in the same state')
    for process in og_ast.processes:
        for ns in [t.inputString.lower() for t in process.terminators
                if t.kind == 'next_state']:
            if not ns in [s.lower() for s in
                    process.mapping.viewkeys()] + ['-']:
                errors.append(['State definition missing: ' + ns.upper()])
        # TODO: do the same with JOIN/LABEL
    return og_ast, warnings, errors


def parseSingleElement(elem='', string=''):
    '''
        Parse any symbol and return syntax error and AST entry
        Used for on-the-fly checks when user edits text
        and for copy/cut to create a new object
    '''
    assert(elem in ('input_part', 'output', 'decision', 'alternative_part',
            'terminator_statement', 'label', 'task', 'procedure_call',
            'text_area', 'state', 'start', 'end', 'procedure'))
    LOG.debug('Parsing string: ' + string)
    parser = parser_init(string=string)
    parser_ptr = getattr(parser, elem)
    assert(parser_ptr is not None)
    syntax_errors = []
    semantic_errors = []
    warnings = []
    t = None
    if parser:
        with samnmax.capture_ouput() as (stdout, stderr):
            r = parser_ptr()
        for e in stderr:
            syntax_errors.append(e.strip())
        for w in stdout:
            syntax_errors.append(w.strip())
        # Get the root of the Antlr-AST to build our own AST entry
        root = r.tree
        root.token_stream = parser.getTokenStream()
        backend_ptr = eval(elem)
        # Create a dummy process, needed to place context data
        context = ogAST.Process()
        t, semantic_errors, warnings = backend_ptr(
                                root=root, parent=None, context=context)
    return(t, syntax_errors, semantic_errors, warnings,
            context.terminators)


def parser_init(filename=None, string=None):
    ''' Initialize the parser (to be called first) '''
    try:
        char_stream = antlr3.ANTLRFileStream(filename)
    except (IOError, TypeError):
        try:
            char_stream = antlr3.ANTLRStringStream(string)
        except TypeError:
            raise IOError('Could not parse input')
    lex = lexer.sdl92Lexer(char_stream)
    tokens = antlr3.CommonTokenStream(lex)
    parser = sdl92Parser(tokens)
    return parser


if __name__ == '__main__':
    print 'This module is not callable'
