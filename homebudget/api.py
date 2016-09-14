"""
API DOCUMENTATION
----
## LOGIN
### facebook callback

1. Accept the access token from Facebook OAuth2 provider
2. Setup an account for user

## BUSINESS

"""
import logging
from time import time

from hashids import Hashids

from pyramid.httpexceptions import HTTPFound, HTTPBadRequest, HTTPNotFound
from pyramid.view import view_config, view_defaults

from .models import (Category,
                     Entry,
                     User
                     )

log = logging.getLogger(__name__)

hasher = Hashids(min_length=16)

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


@view_config(route_name='api_settings', renderer='json', request_method='GET')
def get_settings(request):
    """

    :param request:
    :return:
    """
    return {
        'categories': [
            {'id': 'cat01', 'label': 'Housing'}
        ]
    }


@view_defaults(route_name='api_categories', renderer='json')
class CategoriesRESTView(object):

    def __init__(self, request):
        self.request = request
        self.access_key = request.headers.get('x-access-key', None)

        if self.access_key is None:
            raise HTTPBadRequest()

    @view_config(request_method='GET')
    def query(self):
        """

        :param request:
        :return:
        """
        categories = self.request.db.query(Category)
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
        data['access_key'] = '0'

        category = Category(**data)
        self.request.db.add(category)

        return {
            'category': category.to_dict()
        }


@view_defaults(route_name='api_entries', renderer='json')
class EntriesRESTView(object):

    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def get(request):
        """

        :param request:
        :return:
        """
        return {
            'expenses': [
                {'id': 'cat01', 'category': 'cat01', 'amount': 10}
            ],
            'incomes': [
                {'id': 'cat01', 'category': 'cat01', 'amount': 10}
            ]
        }
