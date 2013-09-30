keynames = {
    '^m': 'enter',
    '^a': 'home',
    '^d': 'delete',
    '^e': 'end',
    '^c': 'copy',
    '^i': 'tab',
    '^k': 'delete_to_end_of_line',
    '^n': ['end', 'enter'],
    '^o': 'open',
    '^p': 'paste',
    '^q': 'quit',
    '^w': 'write',
    '^u': 'undo',
    '^v': 'view_files',
    '^r': 'search_backward',
    '^s': 'search_forward'}

doubles = {
    '^x': {'^u': 'redo',
           '^w': 'write_as',
           '^n': ['up', 'end', 'enter']},
    '^b': {'^b': 'mark'}}

again = {'delete_to_end_of_line'}

repeat = {'home', 'end'}
