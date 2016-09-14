"""
API DOCUMENTATION
----
## LOGIN
### facebook callback

1. Accept the access token from Facebook OAuth2 provider
2. Setup an account for user

## BUSINESS

"""
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config, view_defaults


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

    @view_config(request_method='GET')
    def get(request):
        """

        :param request:
        :return:
        """
        return {
            'categories': [
                {'id': 'cat01', 'label': 'Housing'}
            ]
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
