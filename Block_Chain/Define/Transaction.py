import hashlib


class Transaction(object):

    SUCCESS = 0
    FAIL = 1
    VERIFY = 2

    def __init__(self, timestamp, data, gas_price):
        self.timestamp = timestamp
        self.data = data
        self.gas_price = gas_price
        self.status = None
        self.hash = None

    def transaction_hash(self):
        sha = hashlib.sha256()
        sha.update((
            str(self.data) +
            str(self.timestamp) +
            str(self.gas_price) +
            str(self.status)
        ).encode())
        return sha.hexdigest()
