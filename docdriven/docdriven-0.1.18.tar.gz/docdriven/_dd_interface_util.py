import string
def title2filename(title):
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    filename_safe = title.replace('/', '1l')
    filename_safe = filename_safe.replace(' ', '_')
    filename_safe = "".join(c for c in filename_safe if c in valid_chars).rstrip()
    return filename_safe.lower()
