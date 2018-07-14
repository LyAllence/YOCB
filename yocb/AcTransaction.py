import hashlib


class AcTransaction(object):

    def __init__(self):
        self.address = None
        self.timestamp = None
        self.transaction_hash = None
        self.gas_consume = None
        self.gas_origin = None
        self.gas_add = None
        self.hash = None

    # generate ac transaction hash
    def ac_transaction_hash(self):
        sha = hashlib.sha256()
        sha.update((str(self.address) +
                    str(self.timestamp) +
                    str(self.transaction_hash) +
                    str(self.gas_consume) +
                    str(self.gas_origin) +
                    str(self.gas_add)).encode()
                   )
        return sha.hexdigest()

    @staticmethod
    # parse a ac transaction
    def json_parse(ac_transaction):
        return {
            'address': ac_transaction.address,
            'timestamp': ac_transaction.timestamp,
            'transaction_hash': ac_transaction.transaction_hash,
            'gas_consume': ac_transaction.gas_consume,
            'gas_origin': ac_transaction.gas_origin,
            'gas_add': ac_transaction.gas_add,
            'hash': ac_transaction.hash,
        }

    @staticmethod
    # load a ac transaction
    def json_load(ac_dict):
        ac_transaction = AcTransaction()
        ac_transaction.address = ac_dict['address']
        ac_transaction.timestamp = ac_dict['timestamp']
        ac_transaction.transaction_hash = ac_dict['transaction_hash']
        ac_transaction.gas_consume = ac_dict['gas_consume']
        ac_transaction.gas_origin = ac_dict['gas_origin']
        ac_transaction.gas_add = ac_dict['gas_add']
        ac_transaction.hash = ac_dict['hash']
        return ac_transaction

    @staticmethod
    # add a ac transaction
    def append_ac_transaction(address, timestamp, transaction_hash=None, gas_consume=None, gas_origin=None, gas_add=None):
        ac_transaction = AcTransaction()
        ac_transaction.address = address
        ac_transaction.timestamp = timestamp
        ac_transaction.transaction_hash = transaction_hash
        ac_transaction.gas_consume = gas_consume
        ac_transaction.gas_origin = gas_origin
        ac_transaction.gas_add = gas_add
        ac_transaction.hash = ac_transaction.ac_transaction_hash()
        return ac_transaction

    @staticmethod
    # return a ac transaction
    def obtain_ac_transaction(ac_address, ac_hash, block):
        if not ac_hash or not ac_address:
            return 400, 'Error: your address\'s norm is not accepted!'
        if ac_address in block.ac_transactions:
            if ac_hash in block.ac_transactions.get(ac_address):
                return 200, block.ac_transactions.get(ac_address).get(ac_hash)
            return 400, 'Error: the hash is invalid!'
        return 400, 'Error: the address is invalid, please check your hash!'
