class Pool(object):
    def __init__(self):
        self.auth = None
        self.api = None
        self.storage = None
        self.websocket = None

        self.pool_id = None
        self.pool_xtype = None
        self.pool_ytype = None
        self.data_object = None

    def attach(self, auth=None, api=None, storage=None, websocket=None):
        '''attach all required modules to class object'''
        self.auth = auth
        self.api = api
        self.storage = storage
        self.websocket = websocket

    def select_pool(self, pool_name=None, pool_key=None):
        '''select pool to work in, with either pool_name or pool_key'''
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
                catagory {
                    catagory
                    xtype {
                    data
                    }
                    ytype {
                    data
                    }
                }
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

        self.data_object = data[0]
        self.pool_id = self.data_object['id']
        self.pool_xtype = self.data_object['catagory']['xtype']
        self.pool_ytype = self.data_object['catagory']['ytype']

    def get_backlog(self, limit=100):
        '''get backlog of already completed samples'''
        if not self.auth:
            raise UserWarning(
                "No auth object attached.")

        if not self.pool_id:
            raise UserWarning(
                "Not connected to a pool")

        query = """query ListSamples(
                        $filter: ModelsampleFilterInput
                        $limit: Int
                        $nextToken: String
                    ) {
                        listSamples(filter: $filter, limit: $limit, nextToken: $nextToken) {
                        items {
                            id
                            x
                            y
                        }
                        nextToken
                        }
                    }"""

        params = {
            "filter": {"poolID": {"eq": self.pool_id}, "labeledStatus": {"eq": "COMPLETED"}},
            "limit": limit
        }

        print(self.pool_id)

        response = self.api.execute_gql(query, params)

        try:
            data = response['data']['listSamples']['items']
        except:
            raise UserWarning(
                response['errors'][0]['message'])

        if len(data) == 0:
            raise UserWarning('No Samples found')

        if response['data']['listSamples']['nextToken']:
            print('There are more samples available, try increasing the limit')

        return data

    def connect(self):
        self.websocket.connect(self.pool_id)

    def disconnect(self):
        self.websocket.disconnect()

    def query(self):
        return self.websocket.query()

    def map_output(self, output):
        '''will map output to correct format given by the data-types'''
        return output
