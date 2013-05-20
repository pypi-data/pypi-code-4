#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int

    This module is responsible for rendering SDL AST to a scene.
    It is separated from the main SDL_Scene class as the rendering can
    be done on any scene (e.g. clipboard).

    There is one rendering function per main SDL construct:
    - whole process
    - terminators
    - inputs
    - text areas
    - ...

    This rendering capability is separated from the AST definition (ogAST.py)
    so that the AST module is kept independent from any graphical backend and
    is not related to Pyside.

    When rendering a (set of) symbol(s), update text autocompletion list(s).
"""

import ogAST
import sdlSymbols
import logging

LOG = logging.getLogger(__name__)


def render_process(scene, ast):
    ''' Render a complete SDL process from the AST '''
    top_level_symbols = []

    # Set autocompletion lists for input, output, state, types, variables:
    try:
        sdlSymbols.TextSymbol.completion_list = {
                t.replace('-', '_') for t in ast.dataview}
    except (AttributeError, TypeError):
        LOG.debug('No dataview for filling types autocompletion list')
    sdlSymbols.State.completion_list = {
            state for state in ast.mapping if state != 'START'}
    sdlSymbols.Input.completion_list = {
            signal['name'] for signal in ast.input_signals}
    sdlSymbols.Output.completion_list = {
            signal['name'] for signal in ast.output_signals}
    sdlSymbols.Task.completion_list = set(ast.variables.keys())

    #sdlSymbols.ProcedureCall.completion_list = set(ast.procedures.keys())
    sdlSymbols.ProcedureCall.completion_list = {
            proc.inputString for proc in ast.procedures}

    # Render text areas (DCL declarations, etc.)
    top_level_symbols.extend(
            [render_text_area(scene, text) for text in ast.textAreas])

    # Render procedures (don't create the subscene here)
    top_level_symbols.extend(
            [render_procedure(scene, proc, subscene=proc)
                            for proc in ast.inner_procedures
                            if not proc.external])

    # Render the start symbol
    if ast.start:
        if isinstance(ast, ogAST.Process):
            top_level_symbols.append(
                    render_start(scene, ast.start, ast.states))
        elif isinstance(ast, ogAST.Procedure):
            top_level_symbols.append(
                    render_procedure_start(scene, ast.start, ast.states))

    # Render floating labels
    for label in ast.floating_labels:
        new_label = render_floating_label(scene, label, ast.states)
        top_level_symbols.append(new_label)

    # Render floating states
    for state in ast.states:
        # Create only floating states
        try:
            new_state = render_state(scene, state, ast.terminators, ast.states)
        except TypeError:
            # Discard terminators (see render_state function for explanation)
            pass
        else:
            top_level_symbols.append(new_state)
    return top_level_symbols


def render_state(scene, ast, terminators, states):
    ''' Render a floating state and its inputs '''
    # Discard the state if it is a terminator too as it is not a floating
    # state in that case: it will be rendered together with all its (possible)
    # INPUT children in the render_terminator function.
    for term in terminators:
        if(term.kind == 'next_state' and
                term.pos_x == ast.pos_x and
                term.pos_y == ast.pos_y and
                term.inputString == ast.inputString):
            raise TypeError('This state is a terminator')
    new_state = sdlSymbols.State(parent=None, ast=ast)
    if new_state not in scene.items():
        scene.addItem(new_state)

    for inp in ast.inputs:
        render_input(scene, inp, new_state, states)
    return new_state


def render_text_area(scene, ast):
    ''' Render a text area from the AST '''
    text = sdlSymbols.TextSymbol(ast)
    scene.addItem(text)
    return text


def render_start(scene, ast, states):
    ''' Add the start symbol to a scene '''
    start_symbol = sdlSymbols.Start(ast)
    scene.addItem(start_symbol)
    if ast.transition:
        render_transition(scene, parent=start_symbol,
                ast=ast.transition,
                states=states)
    return start_symbol


def render_procedure(scene, ast, subscene):
    ''' Add a procedure symbol to the scene '''
    proc_symbol = sdlSymbols.Procedure(ast, subscene)
    scene.addItem(proc_symbol)
    return proc_symbol


def render_procedure_start(scene, ast, states):
    ''' Add the procedure start symbol to a scene '''
    start_symbol = sdlSymbols.ProcedureStart(ast)
    scene.addItem(start_symbol)
    if ast.transition:
        render_transition(scene, parent=start_symbol,
                ast=ast.transition,
                states=states)
    return start_symbol

def render_transition(scene, parent, ast, states):
    ''' Add a transition to a scene '''
    for action_symbol in ast.actions:
        parent = render_action(scene, action_symbol, parent, states)

    if ast.terminator:
        render_terminator(scene, ast.terminator, parent, states)


def render_terminator(scene, ast, parent, states):
    ''' Add a terminator (NEXTSTATE, JOIN) to a scene '''
    if ast.label:
        parent = render_action(scene, ast.label, parent, states)
    if ast.kind == 'next_state':
        LOG.debug('ADDING NEXT_STATE ' + ast.inputString)
        # Create a new state symbol
        symbol = sdlSymbols.State(parent=parent, ast=ast)
        # If the terminator is also a new state, render the inputs below
        LOG.debug('STATELIST:' + str([st.inputString for st in states]))
        for state_ast in states:
            if (state_ast.inputString == ast.inputString and
                    state_ast.pos_x == ast.pos_x and
                    state_ast.pos_y == ast.pos_y):
                LOG.debug('MERGING TERMINATOR "' + ast.inputString + '"')
                for input_ast in state_ast.inputs:
                    render_input(scene, input_ast, symbol, states)
    elif ast.kind == 'join':
        symbol = sdlSymbols.Join(parent, ast)
    elif ast.kind == 'stop':
        symbol = sdlSymbols.ProcedureStop(parent, ast)
    else:
        raise TypeError('Unsupported terminator: ' + repr(ast))
    return symbol


def render_action(scene, action, parent, states):
    ''' Render an action symbol on the scene '''
    if isinstance(action, ogAST.Task):
        symbol = sdlSymbols.Task(parent, ast=action)
    elif isinstance(action, ogAST.Output):
        if action.kind == 'output':
            symbol = sdlSymbols.Output(parent, ast=action)
        elif action.kind == 'procedure_call':
            symbol = sdlSymbols.ProcedureCall(parent, ast=action)
    elif isinstance(action, ogAST.Decision):
        symbol = sdlSymbols.Decision(parent, ast=action)
        # Place the symbol at absolute coordinates
        if not parent:
            symbol.setPos(action.pos_x, action.pos_y)
        for branch in action.answers:
            render_action(scene, branch, symbol, states)
    elif isinstance(action, ogAST.Label):
        symbol = sdlSymbols.Label(parent, ast=action)
    elif isinstance(action, ogAST.Answer):
        symbol = sdlSymbols.DecisionAnswer(parent, ast=action)
        # Place the symbol at absolute coordinates so that if
        # the branch has NEXTSTATEs symbols, they are properly placed
        if not parent:
            symbol.setPos(action.pos_x, action.pos_y)
        if action.transition:
            render_transition(scene, parent=symbol,
                    ast=action.transition,
                    states=states)
    elif isinstance(action, ogAST.Terminator):
        symbol = render_terminator(
                scene, action, parent, states)
    else:
        raise TypeError('Unsupported symbol in branch: ' + repr(action))
    return symbol


def render_floating_label(scene, ast, states):
    ''' Add a Floating label from the AST to the scene '''
    lab = sdlSymbols.Label(parent=None, ast=ast)
    if lab not in scene.items():
        scene.addItem(lab)
    lab.setPos(ast.pos_x, ast.pos_y)
    if ast.transition:
        render_transition(
                scene,
                parent=lab,
                ast=ast.transition,
                states=states)
    return lab


def render_input(scene, i_ast, parent, states):
    ''' Add input from the AST to the scene '''
    # Note: PROVIDED clause is not supported
    inp = sdlSymbols.Input(parent, ast=i_ast)
    if inp not in scene.items():
        scene.addItem(inp)
    if not parent:
        inp.setPos(i_ast.pos_x, i_ast.pos_y)
    if i_ast.transition:
        render_transition(
                scene,
                parent=inp,
                ast=i_ast.transition,
                states=states)
    return inp
