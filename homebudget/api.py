"""
API DOCUMENTATION
----
## LOGIN
### facebook callback

1. Accept the access token from Facebook OAuth2 provider
2. Setup an account for user

## BUSINESS

"""
from os import environ, urandom
import binascii

import logging
from time import time
import jwt
from requests import get

import transaction
from hashids import Hashids

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound, HTTPForbidden
from pyramid.view import view_config, view_defaults

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .models import (Category,
                     Entry,
                     User,
                     setup_new_user
                     )

log = logging.getLogger(__name__)

hasher = Hashids(min_length=16)
JWT_SECRET = environ.get('JWT_SECRET', None) or 's3cr3t'

@view_config(route_name='api_link', renderer='json', request_method='POST')
def link(request):
    """
    Link OAuth token with a user by obtaining a long live token for a given access token

    https://graph.facebook.com/oauth/access_token?
            client_id=APP_ID&
            client_secret=APP_SECRET&
            grant_type=fb_exchange_token&
            fb_exchange_token=EXISTING_ACCESS_TOKEN

    :param request:
    :return:
    """

    data = request.json_body
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
            user = setup_new_user(request.db, user_data)

        user.facebook = dict(id=user_data['id'],
                             access_token=access_token)
        request.db.add(user)

        # Encode the access_key
        # TODO Generate access_key
        payload = {
            'sub': user_data['email'],
            'exp': int(time()) + 3600, # expires in one hour
            'access_key': user.access_key
        }
        encoded_payload = jwt.encode(payload, JWT_SECRET)

        return {
            'jwt': encoded_payload
        }


@view_config(route_name='api_quota', renderer='json', request_method='GET')
def quota(request):
    """
    Return the quota for user because each free account should have a limited
    amount of categories, spending entries a day

    :param request:
    :return:
    """
    return {
        'categories': 30,
        'daily_spendings': 50
    }


@view_defaults(route_name='api_settings', renderer='json')
class SettingsRESTView(object):

    def __init__(self, request):
        self.request = request
        if not request.current_user:
            raise HTTPBadRequest()
        self.access_key = str(request.current_user['access_key'])

    @view_config(request_method='GET')
    def get_settings(self):
        """

        :param request:
        :return:
        """
        request = self.request
        user = request.db.query(User).get(request.current_user['id'])

        return {
            'settings': dict(currency=user.currency)
        }

    @view_config(request_method='POST')
    def post(self):
        """

        :param request:
        :return:
        """
        request = self.request

        if request.current_user is None:
            raise HTTPForbidden()

        access_key = request.headers.get('x-access-key', None)
        if access_key is None:
            raise HTTPBadRequest()

        user = request.db.query(User).get(request.current_user['id'])

        data = request.json_body
        settings = data['settings']

        user_has_changed = False
        if 'currency' in settings:
            user.currency = settings['currency']
            user_has_changed = True

        if user_has_changed:
            request.db.add(user)


        return {
            'settings': dict(currency=user.currency)
        }


@view_defaults(route_name='api_categories', renderer='json')
class CategoriesRESTView(object):

    def __init__(self, request):
        self.request = request

        if not request.current_user:
            raise HTTPBadRequest()
        self.access_key = str(request.current_user['access_key'])

    @view_config(request_method='GET')
    def query(self):
        """

        :param request:
        :return:
        """
        categories = self.request.db.query(Category).filter(Category.access_key==self.access_key)
        q = self.request.GET.get('q', None)
        if q is None:
            log.warn('query is empty')

        return {
            'categories': [item.to_dict() for item in categories]
        }

    @view_config(route_name='api_categories_id', request_method='GET')
    def get(self):
        id_ = self.request.matchdict.get('id')
        category = self.request.db.query(Category).get(id_)

        if category is None:
            raise HTTPNotFound()
        if category.access_key != self.access_key:
            raise HTTPNotFound()

        return {
            'category': category.to_dict()
        }

    @view_config(request_method='POST')
    def post(self):
        """

        :param request:
        :return:
        """
        data = self.request.json_body
        data['id'] = hasher.encode(int(time()))
        data['access_key'] = self.access_key

        category = Category(**data)
        self.request.db.add(category)

        return {
            'category': category.to_dict()
        }


@view_defaults(route_name='api_entries', renderer='json')
class EntriesRESTView(object):

    def __init__(self, request):
        self.request = request
        if not request.current_user:
            raise HTTPBadRequest()

        self.access_key = str(request.current_user['access_key'])
        self._query = request.db.query(Entry)

    @view_config(request_method='GET')
    def query(self):
        query = self.request.db.query(Entry).options(joinedload('category'))
        query = query.filter(Entry.access_key == self.access_key)

        q = self.request.GET.get('q', None)
        if q is None:
            log.warn('query is empty')

        return {
            'entries': [item.to_dict(dict(category_label=item.category.label if item.category is not None else 'Income')
                                     ) for item in query]
        }

    @view_config(route_name='api_entries_id', request_method='GET')
    def get(self):
        """

        :param request:
        :return:
        """
        id_ = self.request.matchdict.get('id', None)
        query = self._query.filter(Entry.access_key == self.access_key and Entry.id == id_)

        try:
            entry = query.one()

            return {
                'entry': entry.to_dict()
            }
        except MultipleResultsFound:
            pass
        except NoResultFound:
            raise HTTPNotFound()

    @view_config(request_method='POST')
    def post(self):
        """

        :return:
        """
        data = self.request.json_body
        data['access_key'] = self.access_key

        entry = Entry(**data)
        self.request.db.add(entry)
        with transaction.manager:
            self.request.db.commit()

            self.request.db.refresh(entry)
            return {
                'entry': entry.to_dict(dict(category_label=entry.category.label))
            }
