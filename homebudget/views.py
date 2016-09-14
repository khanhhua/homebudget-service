import logging

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.view import view_config

from requests import get

log = logging.getLogger(__name__)

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
    code = request.GET.get('code', None)
    if code is None:
        raise HTTPBadRequest()

    client_id = '1771952326416166'
    redirect_uri = 'http://localhost:6543/auth/facebook'
    client_secret = '5e87e4e35fd358f7b635bdffb81906cc'

    access_token_url = 'https://graph.facebook.com/v2.7/oauth/access_token'

    response = get(access_token_url, params=dict(code=code,
                                                 client_id=client_id,
                                                 redirect_uri=redirect_uri,
                                                 client_secret=client_secret))

    # see https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow/
    # {
    #   "access_token": {access-token},
    #   "token_type": 	{type},
    #   "expires_in":	{seconds-til-expiration}
    # }
    data = response.json()
    if 'access_token' in data:
        access_token = data['access_token']
        log.debug('access token: %s' % (access_token, ))

        user_profile_url = 'https://graph.facebook.com/v2.7/me?fields=id,name,email'
        response = get(user_profile_url, params=dict(access_token=access_token))

        user_data = response.json()
        log.info(str(user_data))

        from .models import User
        user = request.db.query(User).get(user_data['email'])
        if user is None:
            user = User(id=user_data['email'],
                        name=user_data['name'])
        user.facebook = dict(id=user_data['id'],
                             access_token=access_token)
        request.db.add(user)

        request.session['access_token'] = access_token
        return HTTPFound(location='/')

    else:
        raise HTTPBadRequest()