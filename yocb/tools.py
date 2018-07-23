from yocb.chain_struct.Block import Block
from yocb.chain_struct.Account import Account
from yocb.chain_struct.Node import Node
from yocb.chain_struct.Transaction import Transaction
from yocb.chain_struct.AcTransaction import AcTransaction
import json
from datetime import datetime
import sys
import subprocess
import logging
import os
import root
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from urllib.parse import urlencode
import requests
import getopt
import hashlib

_variable = {}
_variable.setdefault('local_node', None)
_variable.setdefault('agent_nodes', [])
_variable.setdefault('child_nodes', {})
_variable.setdefault('synchronized_block', [])
_variable.setdefault('storage_block', None)
_variable.setdefault('confirming_transaction', {})
_variable.setdefault('confirmed_transaction', {})
_variable.setdefault('ip', None)
_variable.setdefault('port', None)
_variable.setdefault('datadir', None)


class Tool(object):

    # get args' value base from a key with you provide
    @staticmethod
    def get_opt_number(key):

        opts = []
        try:
            opts, args = getopt.getopt(sys.argv[1:], "hipd:", ["help", "ip=", "port=", "datadir="])
        except getopt.GetoptError:
            logging.info('your option is invalid')
            opts.append(('-h', ''))
        opts_ = {i[0]: i[1] for i in opts}
        if '-h' in opts_ or '--help' in opts_:
            sys.stdout.write(
                'Welcome to the YOCB block chain. \n' +
                'Usage: python3 run.py --datadir/-d path [opt]\n' +
                '"path" is genesis.json\'s path \n' +
                'opt:\n' +
                '   -h/--help    get usage of the software.\n' +
                '   -i/--ip ip   set your ip, if you not provide it, we set it to 0.0.0.0.\n' +
                '   -p/--port    set your port, if you not provide it, we set it to 9527.\n'
            )
            exit(0)
        if key in opts_:
            return opts_.get(key)
        return None

    # generate md5 for message
    @staticmethod
    def generate_md5(info_message):
        md5 = hashlib.md5()
        md5.update(info_message)
        return md5.hexdigest()

    # return local _variable
    @staticmethod
    def get_variable():
        return _variable

    # initial all variable
    @staticmethod
    def init_variable():
        try:
            node = Node()
            node.address = 'http://{}:{}'.format(_variable['ip'], _variable['port'])
            node.description = 'this is a common node with address is $address'
            node.timestamp = str(datetime.now())
            node.status = 'agent'
            node.hash = node.node_hash()
            _variable['local_node'] = node
            _variable['agent_nodes'] = [_variable['local_node']]
            _variable['storage_block'] = Block.generate_block(_variable['synchronized_block'][-1])
            return 200, 'all ok'
        except BaseException as e:
            sys.stdout.write(e.args[0])
            sys.exit(1)


class Logger(object):

    # start log service and mode is error
    @staticmethod
    def error_logger():
        logging.basicConfig(level=logging.ERROR,
                            filename=os.path.join(root.get_log(), 'error.log'),
                            filemode='a',
                            format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
                            datefmt='%Y-%m-%d %A %H:%M:%S',
                            )

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  # 定义该handler格式
        console.setFormatter(formatter)
        # Create an instance
        logging.getLogger().addHandler(console)

    # start log service and mode is info
    @staticmethod
    def info_logger():
        logging.basicConfig(level=logging.INFO,
                            filename=os.path.join(root.get_log(), 'service.log'),
                            filemode='w',
                            format='%(asctime)s  %(filename)s : %(levelname)s  %(message)s',  # 定义输出log的格式
                            datefmt='%Y-%m-%d %A %H:%M:%S',
                            )

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  # 定义该handler格式
        console.setFormatter(formatter)
        # Create an instance
        logging.getLogger().addHandler(console)


class Network(object):

    # send message to specify node with tornado
    @staticmethod
    def send_message_with_tornado(url=None, data=None, method='GET'):

        http_client = AsyncHTTPClient()
        if method == 'GET':
            http_request = HTTPRequest(method='GET', url=url)
        else:
            http_request = HTTPRequest(method='POST', url=url + '?' + urlencode(data))
        http_client.fetch(http_request)

    # send message to specify node with requests
    @staticmethod
    def send_message_with_requests(url, data=None, method='GET'):
        response = None
        if method.startswith('GET'):
            response = requests.get(url)
        elif method.startswith('POST'):
            response = requests.post(url + '?' + urlencode(data))
        return response or 'Http request\'s method is error!'

    # check computer if connect network or not.
    @staticmethod
    def inspect_network(url):
        return subprocess.getstatusoutput('ping -c 1 -i 0 ' + url)


class NodeTools(object):

    # register a node, and need some parameter!
    @staticmethod
    def register(address):
        if _variable['agent_nodes'] < 21:
            _variable['agent_nodes'].append(address)
            if len(_variable['agent_nodes']) > 1:
                _variable['local_node'].pre_node_address = _variable['agent_nodes'][-2]
            _variable['local_node'].status = 'agent'
            _variable['local_node'].agent_nodes_count = len(_variable['agent_nodes'])
            _variable['local_node'].hash = _variable['local_node'].node_hash()

        else:
            nodes = _variable['child_nodes']
            # *****************************************************************************************
            # need to get smallest child nodes' address
            previous_address = '0x3131'
            if previous_address not in nodes:
                nodes[previous_address] = [address, ]
            else:
                nodes[previous_address].append(address)
            _variable['local_node'].status = 'child'
            _variable['local_node'].agent_nodes_count = len(_variable['agent_nodes'])
            _variable['local_node'].child_nodes_count = len(_variable['child_nodes'][previous_address])
            _variable['local_node'].child_nodes_address = _variable['child_nodes'][previous_address]
            _variable['local_node'].hash = _variable['local_node'].node_hash()

        # need send result to all nodes *******************************************************************

    # create local node
    @staticmethod
    def generate_local_node(address, description):
        timestamp = str(datetime.now())
        node = Node.generate_local_node(address, description, timestamp)
        _variable['local_node'] = node

    # If the node is disconnect, we will delete
    @staticmethod
    def inspect_node(address):
        node_group = _variable['child_nodes']
        node_type = 'child'
        if address in _variable['agent_nodes']:
            node_group = _variable['agent_nodes']
            node_type = 'agent'
        status, output = Node.detect(address)
        if status == 400:
            return Node.destroy(_variable['local_node'], address, node_group, node_type)


class BlockTools(object):

    # generate a temporary block, to storage confirmed transaction
    @staticmethod
    def generate_block(pre_block):
        try:
            if pre_block:
                if isinstance(pre_block, Block):
                    _variable['storage_block'] = Block.generate_block(pre_block)
                    return
            raise BaseException(pre_block)
        except BaseException as e:
            logging.error('Generate block failed. Because previous block is error, please let me know, Ct@163.com!')
            logging.error('previous block ' + str(e.args[0]))
            sys.exit(1)

    # create genesis
    @staticmethod
    def genesis(genesis_path):
        genesis_file = os.path.join(genesis_path, 'genesis.json')
        try:
            if genesis_file:
                if os.path.isfile(genesis_file):
                    block = Block.genesis(genesis_file)
                    if isinstance(block, Block):
                        block.synchronized = True
                        _variable['synchronized_block'].append(block)
                        return
            raise BaseException('Genesis is can\'t load, Because your file is be damaged!')
        except BaseException as e:
            logging.error(e.args[0])
            sys.exit(1)

    # synchronized block, append the block to synchronized_block
    @staticmethod
    def append_synchronized_block(block):
        _variable.get('synchronized_block').append(block)

    # rollback block chain, if the block chain is not realizable. your must offer timestamp or range,
    @staticmethod
    def rollback(time):
        history_block_chain = _variable.get('synchronized_block')
        while history_block_chain[-1].compare_block(time):
            history_block_chain.pop()

    # check genesis, if remote file is same as local file,
    @staticmethod
    def inspect_genesis(remote_file):

        def get_hash(file_check):
            file_check = [i.replace(' ', '') for i in file_check]
            file_check = [i.replace('\n', '') for i in file_check]
            file_hash = hashlib.md5()
            for line in file_check:
                file_hash.update(line.strip().encode())
            return file_hash.hexdigest()

        local_file = os.path.join(root.get_root(), 'genesis.json')
        with open(local_file, 'r') as local_file_char:
            return get_hash(local_file_char.readlines()) == get_hash(remote_file)


class TransactionTools(object):

    # generate a transaction
    @staticmethod
    def generate_transaction(address, data, gas):

        # check accounts' balance and gas origin
        gas_consume = None
        gas_origin = None
        transaction = Transaction.generate_transaction(address, str(datetime.now()), data,
                                                       gas, gas_origin, gas_consume)
        pass


class AccountTools(object):

    # inspect account environment
    @staticmethod
    def inspect_environment(path, register, address):
        if not (path and register and address):
            return 400, 'your environment is error!'
        return Account.init_environment(path, register, address)

    # register account
    @staticmethod
    def register(name, address, description, path):
        status, output = AccountTools.inspect_environment(path, register=True, address=address)
        if status == 400:
            return 400, output
        private_key, public_key = Account.generate_keys()
        account = Account.generate_account(name, address, public_key, str(datetime.now()), description)
        Account.save_account(path, address, private_key.decode())
        _variable['storage_block'].accounts[address] = json.dumps(account, default=Account.json_parse)
        # send message to all block chain
