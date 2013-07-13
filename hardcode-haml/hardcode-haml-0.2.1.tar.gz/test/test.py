def test(out):
    # syncing the stack
    # Haml line 1
    out.write('<hello>\n')
    # syncing the stack
    # Haml line 2
    out.write('  <div id="')
    out.write(str("blub"))
    out.write('">\n')
    # syncing the stack
    # Haml line 3
    for i in range(5):
        # syncing the stack
        # Haml line 4
        out.write('    ')
        out.write(str(i))
        out.write('\n')
        # syncing the stack
        # Haml line 5
        out.write('    <div class="')
        out.write(str("world"))
        out.write('">\n')
        # syncing the stack
        # Haml line 6
        out.write('      ')
        out.write(str("as"))
        out.write('\n')
        # syncing the stack
        out.write('    </div>\n')
        # Haml line 7
        out.write('    <div class="')
        out.write(str("test"))
        out.write('"></div>\n')
        # End of Haml file, clearing stack
    out.write('  </div>\n</hello>\n')

if __name__ == '__main__': import sys; test(sys.stdout)
