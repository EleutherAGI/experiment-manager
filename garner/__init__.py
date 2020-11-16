# -*- coding: utf-8 -*-

__version__ = "0.0.3"

# Used with pypi checks and other messages related to pip
_garner_module = "garner"

from .authentication import Auth
from .api import Api, WebSocket
from .storage import Storage

from .pool import Pool

auth = Auth()
api = Api()
storage = Storage()
websocket = WebSocket()

pool = Pool()


def login(username, password=None, pool_name=None, pool_key=None):
    auth.authenticate(username, password)

    storage.attach_auth(auth)
    api.attach_auth(auth)
    websocket.attach_auth(auth)

    pool.attach(auth, api, storage, websocket)

    if pool_name or pool_key:
        pool.select_pool(pool_name, pool_key)


select_pool = pool.select_pool
get_backlog = pool.get_backlog
connect = pool.connect
disconnect = pool.disconnect
query = pool.query
