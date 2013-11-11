from scanner import scanner
from base import Cond
import instructions
import base
import inspect
import re


instruction_map = {}

for name, obj in inspect.getmembers(instructions, inspect.isclass):
    if base.Instruction in inspect.getmro(obj):
        instruction_map[name] = obj


def assemble(lines):

    stripped_lines = filter(lambda x: x, strip_comments(map(str.strip, lines)))

    tokenized_lines = map(scanner.scan, stripped_lines)

    # simple label pass
    labels = {}
    current_address = 1
    for line in tokenized_lines:
        tokens, rest = line
        token_type, value = tokens[0]
        if token_type == 'label':
            labels[value] = current_address

        elif token_type == 'operator':
            current_address += 1

    #actual assemble pass
    assembly = []
    line_number = 0
    for line in tokenized_lines:
        line_number += 1
        tokens, rest = line
        if rest:
            print '[%s]: Tokenizer error near' % line_number, rest
            return

        tokens = iter(tokens)
        condition = Cond.ALWAYS

        try:

            while True:
                token = tokens.next()
                token_type, value = token

                if token_type == 'if':
                    token = tokens.next()
                    token_type, value = token
                    if token_type == 'condition':
                        condition = Cond.fromString(value)
                    else:
                        print 'Your if no sense. Line number:', line_number

                elif token_type == 'operator':

                    instruction = value.lower()

                    # Three params
                    if instruction in ['add', 'addi', 'and', 'andi', 'ld',
                                       'mul', 'muli', 'or', 'ori', 'sll',
                                       'slli', 'sra', 'srai', 'srl', 'srli',
                                       'st', 'sub', 'subi', 'xor', 'xori']:
                        _, a = tokens.next()
                        _, b = tokens.next()
                        _, c = tokens.next()
                        instruction = instruction_map[
                            value.capitalize()](a, b, c)

                    # Two params
                    elif instruction in ['jmp', 'ldi', 'sti', 'stg',
                                         'cmp', 'mv', 'neg', 'not']:
                        maybe_label, a = tokens.next()
                        if maybe_label == 'label':
                            b = labels[a]
                            a = 0
                            print instruction, a, b
                        else:
                            _, b = tokens.next()
                        instruction = instruction_map[value.capitalize()](a, b)

                    # One param
                    elif instruction in ['ldg', 'setg', 'nop']:
                        _, a = tokens.next()
                        instruction = instruction_map[value.capitalize()](a)

                    # No params
                    elif instruction in ['nop', 'ret']:
                        instruction = instruction_map[value.capitalize()]()

                    # special cases
                    elif instruction == 'call':
                        maybe_label, a = tokens.next()
                        if maybe_label == 'label':
                            b = labels[a]
                            a = 0
                        else:
                            _, b = tokens.next()
                        instruction = instruction_map[value.capitalize()](a, b)

                    if instruction.cond == Cond.UNSET:
                        instruction.cond = condition
                    assembly.append(instruction)

        except StopIteration:
            pass

    return assembly


def strip_comments(lines):
    newline_delimitor = '!newline delimitor!'
    joined = newline_delimitor.join(lines)
    stripped = re.sub('(/\*([^*]|(\*+[^*/]))*\*+/)', '', joined)
    return stripped.split(newline_delimitor)


def ascii_binary_to_real_binary(ascii_binary):
    return ''.join(
        [chr(int('0b'+ascii_binary[i:i+8], 2))
            for i in range(0, len(ascii_binary), 8)]
    )
