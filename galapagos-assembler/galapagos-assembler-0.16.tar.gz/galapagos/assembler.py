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

    stripped_lines = strip_comments(map(str.strip, lines))
    tokenized_lines = [(line_number, scanner.scan(line)) for
                       line_number, line in stripped_lines]

    # nop insertion pass
    hot_register = None
    for i, line_tuple in enumerate(tokenized_lines):
        line_number, line = line_tuple
        tokens, rest = line
        token_type, value = tokens[0]
        if token_type == 'operator':
            if value == 'ld':
                hot_register = tokens[1][1]
            else:
                for token in tokens[1:]:
                    token_type, value = token
                    if token_type == 'register' and value == hot_register:
                        tokenized_lines.insert(i, ([('operator', 'nop')], ''))
                        hot_register = None

    # simple label pass
    labels = {}
    current_address = 1
    for line_number, line in tokenized_lines:
        tokens, rest = line
        token_type, value = tokens[0]
        if token_type == 'label':
            labels[value] = current_address

        elif token_type == 'operator':
            current_address += 1

    #actual assemble pass
    assembly = []
    for line_number, line in tokenized_lines:
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
                    prefix = ''
                    if token == ('operator', 'not'):
                        token = tokens.next()
                        token_type, value = token
                        prefix = 'not '
                    if token_type == 'condition':
                        condition = Cond.fromString(prefix + value)
                    else:
                        print 'Your if makes no sense. Line number:',
                        print line_number

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
                        else:
                            _, b = tokens.next()
                        instruction = instruction_map[value.capitalize()](a, b)

                    # One param
                    elif instruction in ['ldg', 'setg']:
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
    line_number_delimitor = '!line number delimitor!'
    lines = [str(line_number) + line_number_delimitor + line for
             line_number, line in enumerate(lines)]
    joined = newline_delimitor.join(lines)
    stripped = re.sub('(/\*([^*]|(\*+[^*/]))*\*+/)', '', joined)
    annotated = filter(lambda x: x[1],
                       [line.split(line_number_delimitor)
                        for line in stripped.split(newline_delimitor)])
    return [(int(line_number), line) for line_number, line in annotated]


def ascii_binary_to_real_binary(ascii_binary):
    return ''.join(
        [chr(int('0b'+ascii_binary[i:i+8], 2))
            for i in range(0, len(ascii_binary), 8)]
    )


def ascii_binary_to_vhdl_code(ascii_binary):

    def zero_pad(string, length):
        return string + "0" * max(length - len(string), 0)

    number_of_instructions = len(ascii_binary)/32

    print "type mem is array (0 to " + str(number_of_instructions + 1) + ")",
    print "of std_logic_vector(16-1 downto 0);"
    print ""
    print "constant hi : mem := ("
    print "    0 => \"0000000000000000\","
    i = 0
    for _ in range(number_of_instructions):
        print "    " + str(i + 1) + "  => \"" + \
            zero_pad(ascii_binary[i * 32: i * 32 + 16], 16) + "\","
        i += 1
    print "    " + str(i + 1) + "  => \"0000000000000000\""
    print ");"

    print "constant lo : mem := ("
    print "    0 => \"0000000000000000\","
    i = 0
    for _ in range(number_of_instructions):
        print "    " + str(i + 1) + "  => \"" + \
            zero_pad(ascii_binary[i * 32 + 16: i * 32 + 32], 16) + "\","
        i += 1
    print "    " + str(i + 1) + "  => \"0000000000000000\""
    print ");"
