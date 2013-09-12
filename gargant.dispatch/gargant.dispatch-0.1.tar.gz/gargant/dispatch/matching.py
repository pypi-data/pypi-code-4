def method_matching(method):
    def _matching(environ):
        environ_method = environ.get('REQUEST_METHOD', 'GET')
        return environ_method.lower() == method
    return _matching


ENVIRON_PATH_MATCHING_LIST_NAME = 'gargant.dispatch.path_matching_list'


def path_matching(matching_list):
    def _matching(environ):
        url_kwargs = {'matching_list': matching_list}
        path_list = environ.get(ENVIRON_PATH_MATCHING_LIST_NAME)
        if not path_list:
            path_info = environ.get('PATH_INFO', '')
            path_list = path_info.split('/')
        if len(path_list) < len(matching_list):
            return None

        for path, matching in zip(path_list, matching_list):
            if matching.startswith('{') and matching.endswith('}'):
                key = matching.strip('{}')
                url_kwargs[key] = path
            else:
                if path != matching:
                    return None

        environ[ENVIRON_PATH_MATCHING_LIST_NAME] = path_list[len(matching_list):]

        return url_kwargs
    return _matching
