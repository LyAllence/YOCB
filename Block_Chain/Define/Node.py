import hashlib


class Node(object):

    MAIN = 0
    REPLICAS = 1

    def __init__(self, address, data, timestamp):
        self.address = address
        self.data = data
        self.timestamp = timestamp
        self.status = None
        self.hash = None

    def node_hash(self):
        sha = hashlib.sha256()
        sha.update((
            str(self.address) +
            str(self.timestamp) +
            str(self.data) +
            str(self.status)
                   ).encode())
        return sha.hexdigest()
