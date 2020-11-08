import requests
import json
import .config

class Api:
    def __init__(self, Auth):
        this.Auth = Auth
        
        this.api_endpoint_url = config["aws_appsync_graphqlEndpoint"]
        this.headers = {
            'Authorization': str(this.Auth.access_token)
        }


        def execute_gql(self, query, params):
            this.Auth.check_token()
            payload_obj = {"query": query, "variables" : params}
            payload = json.dumps(payload_obj)
            response = requests.request("POST", this.api_endpoint_url, data=payload, headers=this.headerss)
            return response
        


        