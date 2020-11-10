

from .authentication import Auth
from .api import Api
from .storage import Storage

from .pool import Pool

auth = Auth()
api = Api()
storage = Storage()


pool = Pool()


def login(username, password=None, pool_name=None, pool_key=None):
    auth.authenticate(username, password)

    storage.attach_auth(auth)
    api.attach_auth(auth)

    pool.attach(auth, api, storage)

    if pool_name or pool_key:
        pool.select_pool(pool_name, pool_key)


select_pool = pool.select_pool
