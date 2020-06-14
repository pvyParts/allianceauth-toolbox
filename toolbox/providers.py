from esi.clients import esi_client_factory
from esi.errors import TokenExpiredError
from esi.models import Token

def get_token(character_id, scopes):
    """
    Helper method to get a token for a specific character with specific scopes
    :return: :class:'esi.models.Token or False
    """
    try:
        return Token.objects.filter(character_id=character_id).require_scopes(scopes)[0]
    except:
        return False

### Stolen from django-esi 2.0 ###
def get_auth_header(token):
    """
    Refresh token and return `Authorization` Header for an authed ESI call
    :param token: :class:'esi.models.Token' to uses for Auth
    :return: Array of headers
    """
    if token and token.expired:
        if token.can_refresh:
            token.refresh()
        else:
            raise TokenExpiredError()
    _headers={'Authorization': 'Bearer ' + token.access_token if token else None}
    return _headers


def get_operation_auth_headers(token, also_return_response=False):
    """
    Refresh token and return :class:'Bravado.client.CallableOperation' `_request_options` paramater for an authed ESI call
    :param token: :class:'esi.models.Token' to uses for Auth
    :param also_return_response: also return the response of an esi call
    :return: _request_options Array
    """
    _headers={'headers':get_auth_header(token), "also_return_response":also_return_response}
    return _headers

class EsiResponseClient:
    def __init__(self, token=None):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = esi_client_factory()  # all groups latest
        return self._client

provider = EsiResponseClient()