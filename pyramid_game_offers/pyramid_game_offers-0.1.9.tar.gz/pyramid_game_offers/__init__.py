def _request_params(*required_keys, **required_params):
    """Variant of request_param predicate that works with multiple params.

    If you need to configure a route or view with more than one
    request_param='xxx' or request_param='xxx=abc' predicate, you can
    use this function instead.  Example use:

       # Matches /example?param1&param2=321 (and optional params)
       config.add_route(
           'example',
           '/example',
           custom_predicates=[_request_params('param1', param2=321)])
    """
    required = set(required_keys)

    def predicate(info, request):
        if not required.issubset(set(request.params)):
            return False

        for key, value in required_params.items():
            if request.params.get(key) != value:
                return False

        return True

    return predicate
