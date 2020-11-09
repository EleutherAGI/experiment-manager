from .api import Api
from .storage import Storage
from .authentication import Auth

auth = Auth()
storage = None
api = None


def login(username, private_key=None, password=None):
    auth.authenticate(username, private_key, password)
    storage = Storage(auth)
    api = Api(auth)
