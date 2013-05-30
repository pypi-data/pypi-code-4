

## This function exists here so that it can be imported and run by unit tests
# without any external dependencies.
def parse_token_data(token_data):
    site = None
    context_variable = None

    if 'on' in token_data:
        on_index = token_data.index('on')
        # We need to make sure that the 'on' token we're evaluating appears
        # at the end of the token data - this could be -1 if they used
        # '... on <site>', or -3 if they used '... on <site> as <foo>'
        if on_index == len(token_data) - 2 or on_index == len(token_data) - 4:
            token_data.pop(on_index)
            site = token_data.pop(on_index)

    if 'as' in token_data:
        as_index = token_data.index('as')
        if as_index == len(token_data) - 2:
            token_data.pop(as_index)
            context_variable = token_data.pop(as_index)

    return (token_data, site, context_variable)
