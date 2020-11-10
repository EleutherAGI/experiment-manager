class Pool(object):
    def __init__(self):
        self.auth = None
        self.api = None
        self.storage = None

    def attach(self, auth=None, api=None, storage=None):
        self.auth = auth
        self.api = api
        self.storage = storage

    def select_pool(self, pool_name=None, pool_key=None):

        if not self.auth:
            raise UserWarning(
                "No auth object attached.")

        query = """query ListPools(
            $filter: ModelPoolFilterInput
            $limit: Int
            $nextToken: String
        ) {
            listPools(filter: $filter, limit: $limit, nextToken: $nextToken) {
            items {
                id
                title
                privateKey
            }
            }
        }"""

        if pool_key:
            params = {
                "filter": {"privateKey": {"eq": pool_key}, "owner": {"eq": self.auth.username}}
            }
        elif pool_name:
            params = {
                "filter": {"title": {"eq": pool_name}, "owner": {"eq": self.auth.username}}
            }
        response = self.api.execute_gql(query, params)

        try:
            data = response['data']['listPools']['items']
        except:
            raise UserWarning(
                response['errors'][0]['message'])

        if len(data) == 0:
            raise UserWarning('No pools found')
        if len(data) > 1:
            raise UserWarning(
                'multiple pools found, please use pool key instead')
        return data[0]
