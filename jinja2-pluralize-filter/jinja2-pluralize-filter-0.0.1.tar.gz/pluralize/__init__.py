from pytils import numeral


def pluralize(number, words):
    # Check if words is a list.
    if not (isinstance(words, list) and len(words)):
        return ''

    # Check number
    try:
        number = int(number)
    except ValueError:
        return words[0]

    return numeral.choose_plural(number, words)