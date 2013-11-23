from markdown import markdown
def joke():
    import os
    root = os.path.dirname(__file__)
    jk = open(os.path.join(root, 'joke.dat')).read().decode('utf-8')
    return markdown(jk)
