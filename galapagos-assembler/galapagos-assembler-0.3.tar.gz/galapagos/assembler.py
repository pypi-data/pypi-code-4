from scanner import scanner
from base import Cond
import instructions
import base
import inspect


instruction_map = {}

for name, obj in inspect.getmembers(instructions, inspect.isclass):
    if base.Instruction in inspect.getmro(obj):
        instruction_map[name] = obj


def assemble(lines):

    tokenized_lines = map(scanner.scan, lines)

    # simple label pass
    labels = {}
    current_address = 0
    for line in tokenized_lines:
        tokens, rest = line
        for token in tokens:
            token_type, value = token
            if token_type == 'label':
                labels[value] = current_address + 1

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
                    if instruction in ['add', 'addi', 'and', 'andi',
                                       'mul', 'muli', 'or', 'ori', 'sll',
                                       'slli', 'sra', 'srai', 'srl', 'srli',
                                       'sub', 'subi', 'xor', 'xori']:
                        _, a = tokens.next()
                        _, b = tokens.next()
                        _, c = tokens.next()
                        instruction = instruction_map[
                            value.capitalize()](a, b, c)

                    # Two params
                    elif instruction in ['call', 'jmp', 'ld', 'ldi',
                                         'st', 'sti', 'stg', 'cmp',
                                         'mv', 'neg', 'not']:
                        _, a = tokens.next()
                        maybe_label, b = tokens.next()
                        if maybe_label == 'label':
                            b = labels[b]
                        instruction = instruction_map[value.capitalize()](a, b)

                    # One param
                    elif instruction in ['ldg', 'setg', 'nop', 'ret']:
                        _, a = tokens.next()
                        instruction = instruction_map[value.capitalize()](a)

                    # No params
                    elif instruction in ['nop', 'ret']:
                        instruction = instruction_map[value.capitalize()]()

                    if instruction.cond == Cond.UNSET:
                        instruction.cond = condition
                    assembly.append(instruction)

        except StopIteration:
            pass

    return assembly


def ascii_binary_to_real_binary(ascii_binary):
    return ''.join(
        [chr(int('0b'+ascii_binary[i:i+8], 2))
            for i in range(0, len(ascii_binary), 8)]
    )
