import re
from functools import wraps

#===============================================================================
# Regex expressions
#===============================================================================
RE_WHITESPACE = re.compile(r'\s*')

#===============================================================================
# Exception classes
#===============================================================================
class LaTeXError(ValueError):
    '''Base class for LaTeX syntax errors'''
    def __init__(self, msg, st, pos):
        super(LaTeXError, self).__init__(msg)
        self.st = st
        self.pos = pos

    def message(self):
        msgs = [type(self).__name__, ': ',
                super(LaTeXError, self).__str__(), '\n']
        lines = self.st.splitlines(keepends=True)

        # Accumulate the position of each line
        accpos = [0] + list(map(len, lines))
        for (line_idx, p) in enumerate(accpos[1:]):
            accpos[line_idx + 1] += accpos[line_idx]
            if self.pos < accpos[line_idx]:
                line_idx -= 1
                break

        # Now that we now that pos is in line_idx, we write all lines before the
        # error
        for i, line in enumerate(lines):
            if i <= line_idx:
                msgs.append(line)
            else:
                break

        # Print a triple caret ^^^ just bellow the error
        lpos = self.pos - accpos[line_idx]
        if msgs[-1][-1] != '\n':
            msgs.append('\n')
        msgs.append(' ' * lpos + '^^^')
        return ''.join(msgs)



#===============================================================================
# Read from ichars
#===============================================================================
def re_match(re, st, pos=0, errormsg=''):
    m = re.match(st, pos)
    if m is None or m.start() != pos:
        raise LaTeXError(errormsg, st, pos)
    return st[m.start():m.end()], m.end()

def read_whitespace(st, pos=0, retpos=False):
    ws, pos = re_match(RE_WHITESPACE, st, pos, 'whitespace expected!')
    if retpos:
        return ws, pos
    else:
        return ws

def read_group(st, pos=0, bgroup='{', egroup='}', strip=False, retpos=False):
        '''Read a command in the beginning of sequence of chars. Return a 
        string with the command. Return a tuple (pos, group) with the new cursor 
        and a string with the contents of the group. 
        
        If strip is True, remove any whitespaces and the leading and trailing 
        braces.'''

        b_ws, pos = read_whitespace(st, pos, True)

        # Search for closing group
        if st[pos] != bgroup:
            raise LaTeXError('missing %r' % bgroup, st, pos)

        # Matched group delimiters are closed on the second occurrence of the
        # delimiter
        if bgroup == egroup:
            end_pos = st.find(egroup, pos + 1)
            group = st[pos:end_pos + 1]
            pos = end_pos + 1

        # Different delimiters must be matched
        else:
            bgroup_n = egroup_n = 0
            for idx in range(pos + 1, len(st)):
                c = st[idx]
                if c == bgroup:
                    bgroup_n += 1
                elif c == egroup:
                    egroup_n += 1
                if egroup_n > bgroup_n:
                    group = st[pos:idx + 1]
                    pos = idx + 1
                    break
            else:
                raise LaTeXError('EOF before %r!' % egroup, st, idx)

        # Match trailing whitespace
        e_ws, pos = read_whitespace(st, pos, True)

        if not strip:
            group = b_ws + group + e_ws
        else:
            group = group[len(bgroup):-len(egroup)]

        return ((group, pos) if retpos else group)

def read_altarg(st, pos=0, bgroup='[', egroup=']', strip=False, retpos=False, require=False):
    try:
        return read_group(st, pos, bgroup, egroup, strip, retpos)
    except LaTeXError as e:
        if e.pos == pos:
            return None, pos

def goto_sub(st, sub, pos=0):
    pos = st.find(sub, pos)
    if pos != -1:
        return pos
    else:
        raise ValueError('substring not found: %r' % sub)

RE_ANY_CMD = {}

def goto_any(st, sub_list, pos=0):
    try:
        regex = RE_ANY_CMD[tuple(sub_list)]
    except KeyError:
        regex = '(%s)' % '|'.join(re.escape(cmd) for cmd in sub_list)
        RE_ANY_CMD[tuple(sub_list)] = regex = re.compile(regex)

    m = regex.search(st, pos)
    if m:
        value = st[m.start():m.end()]
        return value, m.start()
    else:
        raise ValueError('no substrings found')

def read_any(st, sub_list, pos=0):
    try:
        sub, new_pos = goto_any(st, sub_list, pos)
    except ValueError:
        return st[pos:], None, -1
    else:
        pre = st[pos:new_pos]
        return pre, sub, new_pos + len(sub)

if __name__ == '__main__':
    try:
        tex = r'oh yeah\foo, \bar'
        print(goto_sub(tex, '\\foo'))
        print(goto_any(tex, ['\\foo', '\\bar']))

        print(read_group(' {foo} \\bar'))
        st = ' {foo \\bar{1}} {\\bar}'
        a, pos = read_group(st, retpos=True)
        b = read_group(st, pos)
        print([a, b])
    except LaTeXError as e:
        print(e.message())

