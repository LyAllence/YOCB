from config import block_size_limit, block_gas_limit
import hashlib


class Block(object):
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = None
        self.data = data
        self.previous_hash = previous_hash
        self.transaction = []
        self.gas_limit = block_gas_limit
        self.block_size = block_size_limit
        self.contract_data = {}
        self.have_sync = False
        self.account = {}
        self.account_transaction = {}
        self.hash = None

    def hash_block(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) +
                    str(self.timestamp) +
                    str(self.data) +
                    str(self.previous_hash) +
                    str(self.gas_limit) +
                    str(self.block_size) +
                    str(self.contract_data) +
                    str(self.account_transaction) +
                    str(self.account)
                    ).encode())
        return sha.hexdigest()

