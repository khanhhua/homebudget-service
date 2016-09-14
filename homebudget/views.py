from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name='home', renderer='templates/home.html')
def home(request):
    return {'project': 'HomeBudget'}


@view_config(route_name='facebook_callback')
def facebook_callback(request):
    """
    1. Accept the access token from Facebook OAuth2 provider
    2. Setup an account for user

    :param request:
    :return:
    """
    return HTTPFound(location='/home')
