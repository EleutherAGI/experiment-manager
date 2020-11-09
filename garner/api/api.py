import requests
import json
from ..config import config


class Api:
    def __init__(self, Auth):
        self.Auth = Auth

        self.api_endpoint_url = config["aws_appsync_graphqlEndpoint"]
        self.headers = {
            'Authorization': str(self.Auth.access_token)
        }

        def execute_gql(self, query, params):
            self.Auth.check_token()
            payload_obj = {"query": query, "variables": params}
            payload = json.dumps(payload_obj)
            response = requests.request(
                "POST", self.api_endpoint_url, data=payload, headers=self.headerss)
            return response
