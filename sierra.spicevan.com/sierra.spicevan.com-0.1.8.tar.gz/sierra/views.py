from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/home.pt')
def home_view(request):
    return {'project': 'sierra'}


@view_config(route_name='abc', renderer='templates/abc.pt')
def abc_view(request):
    return {'project': 'sierra'}
