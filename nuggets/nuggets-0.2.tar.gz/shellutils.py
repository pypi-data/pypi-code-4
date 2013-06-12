import sys
from termios import tcflush, TCIOFLUSH


def yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    Args:
        ``question``: is a string that is presented to the user.
        ``default``: is the presumed answer if the user just hits <Enter>.
                 It must be "yes" (the default), "no" or None (meaning
                 an answer is required of the user).

    Returns:
        True iff the user entered yes.
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        tcflush(sys.stdin, TCIOFLUSH)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
