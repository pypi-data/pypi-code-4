"""Yesno question with default answer"""

def yesno(message, default='y'):
    """Poses a simple yes/no question and waits for the user reaction"""
    # convert boolean default to string
    if isinstance(default, bool):
        default = "y" if default else "n"
    choices = 'Y/n' if default.lower() in ('y', 'yes') else 'y/N'
    choice = raw_input("%s (%s) " % (message, choices))
    values = ('y', 'yes', '') if default == 'y' else ('y', 'yes')
    return choice.strip().lower() in values
        

