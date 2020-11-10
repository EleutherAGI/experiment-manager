import requests
import json
from ..config import config
from .exceptions import *


class Api(object):
    def __init__(self, Auth=None):

        self.Auth = Auth

        self.api_endpoint_url = config["aws_appsync_graphqlEndpoint"]
        self.headers = None

    def attach_auth(self, auth):
        self.Auth = auth

        self.headers = {
            'Authorization': str(self.Auth.access_token)
        }

    def execute_gql(self, query, params):

        if not self.headers:
            raise NoAuthException(
                "No auth object attached.")

        self.Auth.check_token()
        payload_obj = {"query": query, "variables": params}
        payload = json.dumps(payload_obj)

        try:
            response = requests.request(
                "POST", self.api_endpoint_url, data=payload, headers=self.headers)

            return response.json()

        except requests.exceptions.Timeout:
            raise TimeOutException(
                "Request timed out")
        except requests.exceptions.TooManyRedirects:
            raise TooManyRedirectsException(
                "Too many Redirects")
        except requests.exceptions.RequestException as e:
            raise GenericRequestException(
                "Request raised error {}".format(e))
