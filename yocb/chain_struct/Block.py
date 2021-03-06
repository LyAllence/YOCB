import hashlib
import json
from datetime import datetime


class Block(object):
    def __init__(self):
        self.index = 0
        self.pre_block_hash = None
        # timestamp is must be dumped by json
        self.timestamp = None
        self.version = '#version1'
        self.block_max_size = 5000
        self.synchronized = False
        # key is address, value is user's data, the data is must be dumped by json
        self.accounts = {}
        # key is transaction's hash, value is a transaction, be similar to account's transaction
        self.transactions = {}
        # key is account's address, value is a map, the inner of map value is transaction's hash
        # and value is account transaction
        # account's transaction
        self.ac_transactions = {}
        self.hash = None

    # create a hash base from variable
    def hash_block(self):
        sha = hashlib.sha256()
        sha.update((str(self.index) +
                    str(self.pre_block_hash) +
                    str(self.timestamp) +
                    str(self.version) +
                    str(self.block_max_size) +
                    str(self.synchronized) +
                    str(self.accounts) +
                    str(self.transactions) +
                    str(self.ac_transactions)
                    ).encode())
        return sha.hexdigest()

    # parse one block
    @staticmethod
    def json_parse(block):
        return {
            'index': block.index,
            'pre_block_hash': block.pre_block_hash,
            'timestamp': block.timestamp,
            'version': block.version,
            'block_max_size': block.block_max_size,
            'synchronized': block.synchronized,
            'accounts': json.dumps(block.accounts),
            'transactions': json.dumps(block.transactions),
            'ac_transactions': json.dumps(block.ac_transactions),
            'hash': block.hash,
        }

    # load block
    @staticmethod
    def json_load(block_dict):
        block = Block()
        block.index = block_dict['index']
        block.pre_block_hash = block_dict['pre_block_hash']
        block.timestamp = block_dict['timestamp']
        block.version = block_dict['version']
        block.block_max_size = block_dict['block_max_size']
        block.synchronized = block_dict['synchronized']
        block.accounts = json.loads(block_dict['accounts'])
        block.transactions = json.loads(block_dict['transactions'])
        block.ac_transactions = json.loads(block_dict['ac_transactions'])
        block.hash = block_dict['hash']
        return block

    # create genesis block from json file
    @staticmethod
    def genesis(genesis_file):
        try:
            with open(genesis_file, 'r') as genesis_file_open:
                block = json.load(fp=genesis_file_open, object_hook=Block.json_load)
                block.timestamp = str(datetime.now())
                block.hash = block.hash_block()
                return block
        except BaseException as e:
            return e.args[0]

    # generate a temporary block
    @staticmethod
    def generate_block(pre_block):
        block = Block()
        block.index = pre_block.index + 1
        block.pre_block_hash = pre_block.hash
        return block

    def __str__(self):
        return json.dumps({
            'index': self.index,
            'version': self.version,
            'hash': self.hash,
            'pre_hash': self.pre_block_hash,
        })

    # compare time, if in range return True, or False
    # time_now is now time, is datetime. old time is block time, is str
    @staticmethod
    def compare_time(block_time, rollback_time):
        block_time = block_time[:block_time.rindex('.')]
        block_time = datetime.strptime(block_time, '%Y-%m-%d %H:%M:%S')
        if '.' in rollback_time:
            rollback_time = rollback_time[:rollback_time.rindex('.')]
        rollback_time = datetime.strptime(rollback_time, '%Y-%m-%d %H:%M:%S')
        return block_time >= rollback_time

    # if the block time is gt rollback, return True
    def compare_block(self, rollback_time):
        return Block.compare_time(self.timestamp, rollback_time)
