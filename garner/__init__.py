from .api import Api
from .storage import Storage
from .authentication import Auth

auth = Auth()
storage = Storage()
api = Api()


def login(username, private_key=None, password=None):
    auth.authenticate(username, private_key, password)
    storage.attach_auth(auth)
    api.attach_auth(auth)
