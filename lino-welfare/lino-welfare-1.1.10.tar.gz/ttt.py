import re
ws_re = re.compile(r'\s+')
target = """foo
bar
x
"""
print ws_re.sub(' ', target)
