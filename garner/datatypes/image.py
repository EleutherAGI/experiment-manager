class Image(object):
    def __init__(self, storage):
        self.storage = storage

    def get(self, raw: []) -> str:
        download_loc = self.storage.download_file(raw[0])
        return download_loc

    def put(self, val: str) -> []:
        key = self.storage.upload_file(val)
        return [key]
