import re

pat1 = re.compile(r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
pat2 = re.compile(r"#(^|[\n ])(((www|ftp)\.[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)


def urlify(value):
    urlstr = pat1.sub(r'\1<a href="\2" target="_blank">\3</a>', value)
    urlstr = pat2.sub(r'\1<a href="http:/\2" target="_blank">\3</a>', urlstr)
    return urlstr
