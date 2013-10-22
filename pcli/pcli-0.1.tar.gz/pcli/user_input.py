"""User input tools."""

def question(message, *args, **kwargs):
    """Questions user. Returns True if user says yes."""

    answer = ""
    while answer not in ("y", "n"):
        answer = input((message + " (y/n) ").format(*args, **kwargs))

    return answer == "y"
