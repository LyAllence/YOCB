import hashlib


class Transaction(object):

    def __init__(self):
        self.timestamp = None
        self.data = None
        self.gas = None
        self.status = 'Verifying'
        self.signature = []
        # origin is block index
        self.gas_origin = None
        # consume is last gas consume in the block
        self.gas_consume = None
        self.address = None
        self.hash = None

    # create local hash
    def transaction_hash(self):
        sha = hashlib.sha256()
        sha.update((
            str(self.timestamp) +
            str(self.data) +
            str(self.gas) +
            str(self.status) +
            str(self.signature) +
            str(self.gas_origin) +
            str(self.gas_consume)
        ).encode())
        return sha.hexdigest()

    # parse a transaction
    @staticmethod
    def json_parse(transaction):
        return {
            'timestamp': transaction.timestamp,
            'data': transaction.data,
            'gas': transaction.gas,
            'status': transaction.status,
            'signature': transaction.signature,
            'gas_origin': transaction.gas_origin,
            'gas_consume': transaction.gas_consume,
            'hash': transaction.hash,
        }

    # load a transaction
    @staticmethod
    def json_load(transaction_dict):
        transaction = Transaction()
        transaction.timestamp = transaction_dict['timestamp']
        transaction.data = transaction_dict['data']
        transaction.gas = transaction_dict['gas']
        transaction.status = transaction_dict['status']
        transaction.signature = transaction_dict['signature']
        transaction.gas_origin = transaction_dict['gas_origin']
        transaction.gas_consume = transaction_dict['gas_consume']
        transaction.hash = transaction_dict['hash']
        return transaction

    # generate a transaction
    @staticmethod
    def generate_transaction(address, timestamp, data, gas, gas_origin, gas_consume):
        transaction = Transaction()
        transaction.address = address
        transaction.timestamp = timestamp
        transaction.data = data
        transaction.gas = gas
        transaction.gas_origin = gas_origin
        transaction.gas_consume = gas_consume
        transaction.hash = transaction.transaction_hash()
        return transaction

    # obtain a transaction of a block, if have no, return 400, or 200
    @staticmethod
    def obtain_transaction(transaction_hash, block):
        if not transaction_hash:
            return 400, 'Error: your hash\'s norm is not accepted!'
        if transaction_hash in block.transactions:
                return 200, block.transactions.get(transaction_hash)
        return 400, 'Error: the hash is invalid, please check your hash!'
