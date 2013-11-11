def extract_file_ext(request):
    """
    Extracts file extension either from a request, or enviroment.
    """
    if isinstance(request, basestring):
        mimetype = request
    else:
        mimetype = request.accept_mimetypes.best
    return mimetype.split('/')[1]


def extract_table_name(request):
    """Extracts the table name from the request.path.
    """
    return request.path.split("/")[1]


def is_json_request(request):
    """Returns true is the best accept mimetype is json.
    """
    return extract_file_ext(request) == 'json'


def extract_table_row_id(uri):
    """Returns the table name and row id from a string.
    """
    return uri.split('/')[1:]


def create_response(request, row_id):
    """Creates the post response.
    """
    from db2rest.renderer import Response
    response = None
    if row_id:
        msg = "Resource %d created" % row_id
        response = Response(msg, status="201")
        response.location = "/".join((request.path, str(row_id)))
    return response


def update_response(request, data):
    """Creates a update response.
    """
    from db2rest.renderer import Response
    rowcount, data = data
    response = None
    if data:
        msg = "Resource modified %d, %s created" % (rowcount, data)
        response = Response(msg, status="201")
    return response


def delete_response(request):
    """Creates a delete response.
    """
    from db2rest.renderer import Response
    return Response(status="204")
