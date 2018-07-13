from tornado.web import RequestHandler
from Block_Chain.Chain import Utils
from Block_Chain.Chain import Account_Utils
import json
import logging
from tornado.web import asynchronous
from tornado.gen import coroutine
import tornado.gen as gen


###
# welcome to chain block
###
class MainHandle(RequestHandler):

    def get(self, *args, **kwargs):
        self.write(Utils.NodeNumber)
        self.write('Hello, welcome to here, you can distribute your suggest in your browser!!')


###
# Block Controller
###
class BlockHandle(RequestHandler):

    uri = None
    url = None

    def prepare(self):
        self.uri = self.request.uri

    def get(self, *args, **kwargs):
        if self.uri == '/block/get':
            self.write(Utils.get_have_sync_block())
        if '/block/sync/' in self.uri:
            self.sync_controller(self.uri.replace('/block/sync/', ''))

    def post(self, *args, **kwargs):

        if self.uri.startswith('/block/sync/add'):
            self.post_sync_add()

    @staticmethod
    @coroutine
    def sync_controller(uri_end):

        if uri_end == 'prepare':

            sync_hash = Utils.block_new.hash
            Utils.RequestFlag[sync_hash + 'prepare'] = False
            Utils.SyncFlag = True
            Utils.ResponseNumber[sync_hash + 'prepare'] = 0
            Utils.RequestFlag[sync_hash + 'prepare'] = True
            Utils.SignMap[sync_hash + 'prepare'] = []

            for i in Utils.node:
                Utils.send_message_to_all(url='http://%s/node/request/sync/prepare' % i.address,
                                          method='POST',
                                          data_map={
                                              'local_address': Utils.main_node.address,
                                              'aim_address': Utils.main_node.address,
                                              'hash': sync_hash,
                                          })

    @coroutine
    def post_sync_add(self):
        try:

            local_address = self.get_argument('local_address')
            aim_address = self.get_argument('aim_address')
            temp_hash = self.get_argument('hash')
            new_block = json.loads(self.get_argument(temp_hash),
                                   object_hook=Utils.load_block)

            new_block_transaction = [json.loads(i, object_hook=Utils.load_transaction) for i in new_block.transaction]
            local_block_new_transaction = [json.loads(i, object_hook=Utils.load_transaction)
                                           for i in Utils.block_new.transaction]
            local_new_block_transaction_hash = [i.hash for i in local_block_new_transaction]
            new_block_transaction_hash = [i.hash for i in new_block_transaction]
            for i in new_block_transaction_hash[:]:
                if i in local_new_block_transaction_hash:
                    local_new_block_transaction_hash.pop(local_new_block_transaction_hash.index(i))
                    new_block_transaction_hash.pop(new_block_transaction_hash.index(i))
            if new_block_transaction_hash:
                for i in Utils.transaction_have_verify_cache:
                    if i.hash in new_block_transaction_hash:
                        Utils.transaction_have_verify_cache.pop(Utils.transaction_have_verify_cache.index(i))
            if local_new_block_transaction_hash:
                for i in local_block_new_transaction:
                    if i.hash in local_new_block_transaction_hash:
                        Utils.transaction_have_verify_cache.append(i)

            del new_block_transaction_hash
            del new_block_transaction
            del local_new_block_transaction_hash
            del local_block_new_transaction

            Utils.block_chain_have_sync.append(new_block)
            Utils.create_new_block()
            Utils.SyncFlag = False
            Utils.ChainFlag['sync_flag'] = False

            for i in Utils.node:
                if local_address == i.address:
                    Utils.send_message_to_all(url='http://%s/node/request/sync/commit?aim_address=%s&local_address=%s'
                                              % (i.address, aim_address, Utils.main_node.address))
                else:
                    Utils.send_message_to_all(url='http://%s/block/sync/add' % i.address,
                                              method='POST',
                                              data_map={
                                                  'local_address': Utils.main_node.address,
                                                  'hash': temp_hash,
                                                  temp_hash: json.dumps(obj=Utils.block_new, default=Utils.parse_block),
                                                  'aim_address': aim_address,
                                              })

        except BaseException as e:
            logging.exception(e)


###
# Transaction Controller
###
class TransactionHandle(RequestHandler):

    uri = None

    def prepare(self):
        uri_request = self.request.uri
        if '?' not in uri_request:
            self.uri = uri_request
        else:
            self.uri = uri_request[:uri_request.index('?')]

    def get(self, *args, **kwargs):
        if self.uri == '/transaction/get':
            self.get_transaction()

    def post(self, *args, **kwargs):
        if self.uri.startswith('/transaction'):
            self.post_transaction_controller(uri_end=self.uri.replace('/transaction/', ''))

    @coroutine
    def post_transaction_controller(self, uri_end):
        if uri_end == 'submit':
            self.user_submit_transaction()

    @coroutine
    def user_submit_transaction(self):
        try:

            # verify user
            user_address = self.get_argument('address')
            account_dir = self.get_arguments('dir')
            gas = int(self.get_argument('gas'))

            if gas <= 0:
                raise BaseException('Error: gas is must plus!')

            if account_dir:
                Account_Utils.init_environment(account_dir[0])
            else:
                if Account_Utils.init_environment().startswith('Error'):
                    raise BaseException('Error: your path is not exist or this path have used')

            account_address, private_pem = Account_Utils.load_account()

            if not account_address:
                raise BaseException('Error: you have no register!!')

            if user_address != account_address:
                raise BaseException('Error: you cannot connect chain use this address!!')

            account = Utils.get_account(user_address, Utils.block_chain_have_sync[:])

            if isinstance(account, str):
                raise BaseException('Error: you cannot connect this network!!')

            public_pem = account.signature

            if not Account_Utils.verify_user(public_pem, private_pem):
                raise BaseException('Error: you cannot connect this network!')

            # verify balance
            index_use, gas_use, balance = Utils.get_account_balance(account_address, block=Utils.block_chain_have_sync)
            if balance < gas:
                raise BaseException('Error: your balance is not enough!')

            data = json.loads(self.get_argument('data'))
            data.setdefault('user_address', user_address)
            data.setdefault('public_key', public_pem)
            index, use_gas = Utils.get_index_gas(user_address, Utils.block_chain_have_sync, index_use, gas_use, gas)
            data.setdefault('index', index)
            data.setdefault('use_gas', use_gas)
            temp_hash = Utils.user_submit_transaction(data=json.dumps(data), gas=gas)
            # init environment
            if len(Utils.node) > 0:
                Utils.RequestFlag[temp_hash + 'pre_prepare'] = True
                Utils.ResponseNumber[temp_hash + 'pre_prepare'] = 0
                Utils.SignMap[temp_hash + 'pre_prepare'] = []

            ###
            # send pre_prepare
            ###
            for i in Utils.node:
                Utils.send_message_to_all(url='http://%s/node/request/transaction/pre_prepare' % i.address,
                                          data_map={temp_hash: Utils.transaction_not_verify_cache[temp_hash],
                                                    'local_address': Utils.main_node.address,
                                                    'aim_address': Utils.main_node.address,
                                                    'hash': temp_hash},
                                          method='POST')
            self.write('your transaction is verifying, and your transaction\'s hash is ' + temp_hash)
        except BaseException as e:
            logging.exception(e)
            self.write(e.args[0])

    @coroutine
    def get_transaction(self):
        try:
            hash_temp = self.get_argument('hash')
            self.write(Utils.get_transaction(get_hash=hash_temp, block=Utils.block_chain_have_sync))
        except Exception as e:
            logging.exception(e)
            self.write(e.args[0])


# Miner Controller
class MinerHandle(RequestHandler):

    miner_flag = None

    def prepare(self):
        try:
            self.miner_flag = self.get_argument('flag')
        except BaseException as e:
            logging.exception(e)
            self.write(e.args[0])

    def get(self, *args, **kwargs):
        if self.miner_flag == 'get':
            self.write(str(Utils.ChainFlag['miner_flag']))
        elif self.miner_flag == 'start':
            Utils.ChainFlag['miner_flag'] = True
            self.write('your request is success! and %s miner' % self.miner_flag)
        elif self.miner_flag == 'stop':
            Utils.ChainFlag['miner_flag'] = False
            self.write('your request is success! and %s miner' % self.miner_flag)
        else:
            self.write('you must give a valid value to flag')


# Node Controller
class NodeHandle(RequestHandler):

    uri = None
    url = None

    def prepare(self):
        uri_request = self.request.uri
        if '?' not in uri_request:
            self.uri = uri_request
        else:
            self.uri = uri_request[:uri_request.index('?')]
        self.url = self.request.full_url()

    def post(self, *args, **kwargs):
        if self.uri.startswith('/node/request'):
            self.post_request_transaction(uri_end=self.uri.replace('/node/request/', ''))
        elif self.uri == '/node/user/register/response':
            self.user_register(response=True)

    def get(self, *args, **kwargs):
        if '/node/user/' in self.uri:
            self.node_controller(self.uri.replace('/node/user/', ''))
        elif '/node/request/' in self.uri:
            self.request_controller(self.uri.replace('/node/request/', ''))
        elif self.uri.startswith('/node/response'):
            self.response_controller(self.uri.replace('/node/response/', ''))

    @coroutine
    def post_request_transaction(self, uri_end):
        if uri_end == 'transaction/pre_prepare':
            self.transaction_pre_prepare()
        elif uri_end == 'sync/prepare':
            self.request_sync_prepare()

    @coroutine
    def transaction_pre_prepare(self):
        try:

            request_address = self.get_argument('local_address')
            temp_hash = self.get_argument('hash')
            aim_address = self.get_argument('aim_address')
            transaction_temp = self.get_argument(temp_hash)

            Utils.transaction_not_verify_cache[temp_hash] = transaction_temp
            result = 'permit'
            sign = Utils.get_node_sign(temp_hash + 'pre_prepare')

            for i in Utils.node:
                if i.address == request_address:
                    Utils.send_message_to_all(url='http://%s/node/response/transaction/pre_prepare'
                                                  '?local_address=%s&result=%s&aim_address=%s'
                                                  '&hash=%s&sign=%s'
                                              % (i.address, Utils.main_node.address, result,
                                                 aim_address, temp_hash, sign))
                    continue
                Utils.send_message_to_all(url='http://%s/node/request/transaction/pre_prepare' % i.address,
                                          data_map={temp_hash: transaction_temp,
                                                    'local_address': Utils.main_node.address,
                                                    'aim_address': aim_address,
                                                    'hash': temp_hash},
                                          method='POST')

        except BaseException as e:
            logging.exception(e)

    @coroutine
    def node_controller(self, uri_end):
        if uri_end == 'get':
            self.write(Utils.get_node())
        elif uri_end == 'register':
            self.user_register()
        elif uri_end == 'register/request':
            self.user_register(request=True)
        elif uri_end == 'register/add':
            self.user_register_add()

    @coroutine
    def response_controller(self, uri_end):
        if uri_end == 'sync/prepare':
            self.response_sync_prepare()
        elif uri_end == 'transaction/pre_prepare':
            self.response_transaction_pre_prepare()
        elif uri_end == 'transaction/prepare':
            self.response_transaction_prepare()

    @coroutine
    def request_controller(self, uri_end):
        if uri_end == 'transaction/prepare':
            self.request_transaction_prepare()
        elif uri_end == 'transaction/prepare':
            self.request_transaction_prepare()
        elif uri_end == 'transaction/commit':
            self.request_transaction_commit()
        elif uri_end == 'sync/commit':
            self.request_sync_commit()

    @coroutine
    def user_register_add(self):
        try:

            address = self.get_argument('address')
            hash_temp = self.get_argument('hash')

            if address in Utils.NodeNumber:
                raise BaseException('the node is register in here, please inspect!')
            Utils.NodeNumber[hash_temp] = address
        except BaseException as e:
            logging.exception(e)

    @coroutine
    def user_register(self, response=False, request=False):
        try:
            address = self.get_argument('address')

            if not response and not request:
                Utils.send_message_to_all(url='http://%s/node/user/register/request'
                                              '?address=%s&data=%s&genesis_hash=%s&hash=%s'
                                          % (address, Utils.main_node.address,
                                             Utils.main_node.data, Utils.get_genesis_hash(), Utils.main_node.hash))
                return
            elif request:
                if self.get_argument('genesis_hash') != Utils.get_genesis_hash():
                    self.write('your genesis data is invalid! so you cannot attend this block chain!')
                    return
                data = self.get_argument('data')
                hash_ = self.get_argument('hash')
                hash_temp = Utils.register_node(address=address, data=data, hash_temp=hash_)
                if hash_temp.startswith('Error'):
                    self.write(hash_temp)
                    return
                Utils.NodeNumber.setdefault(hash_temp, address)
                Utils.send_message_to_all(url='http://%s/node/user/register/response' % address,
                                          method="POST",
                                          data_map={
                                              'address': Utils.main_node.address,
                                              'data': Utils.main_node.data,
                                              'block_chain_have_sync': Utils.get_have_sync_block(),
                                              'node': json.dumps(Utils.NodeNumber),
                                              'hash': Utils.main_node.hash,
                                          })

                # add the node in other node
                for i in Utils.node:
                    if i.address == address:
                        continue
                    Utils.send_message_to_all(url='http://%s/node/user/register/add'
                                                  '?address=%s&hash=%s'
                                              % (i.address, address, hash_temp))

                # 同步文件
            elif response:
                hash_temp = self.get_argument('hash')
                data = self.get_argument('data')
                Utils.register_node(address=address, data=data, hash_temp=hash_temp)
                block_chain_have_sync = json.loads(self.get_argument('block_chain_have_sync'))
                node_map = self.get_argument('node')
                hash_temp = self.get_argument('hash')

                Utils.NodeNumber = json.loads(node_map)
                Utils.NodeNumber.pop(Utils.main_node.hash)
                Utils.NodeNumber.setdefault(hash_temp, address)

                Utils.block_chain_have_sync = Utils.load_all_block(block_chain_have_sync[:])
                del block_chain_have_sync
        except BaseException as e:
            logging.exception(e)

    @coroutine
    def response_sync_prepare(self):
        try:

            local_address = self.get_argument('local_address')
            aim_address = self.get_argument('aim_address')
            result = self.get_argument('result')
            response_hash = self.get_argument('hash')
            response_sign = self.get_argument('sign')

            # this is node send this transaction
            if aim_address == Utils.main_node.address:
                Utils.SignMap[response_hash + 'prepare'].append(response_sign)
                Utils.ResponseNumber[response_hash + 'prepare'] += 1
                Utils.ResponseResult[response_sign] = result
                node_count = len(Utils.NodeNumber.keys())
                permit_count = Utils.get_count_from_map(result_map=Utils.ResponseResult,
                                                        key_list=Utils.SignMap[response_hash + 'prepare'])
                # here is stand of request through verify!
                if permit_count >= node_count // 2 and Utils.RequestFlag[response_hash + 'prepare']:

                    Utils.RequestFlag[response_hash + 'prepare'] = False
                    Utils.block_new.have_sync = True
                    Utils.block_new.hash = Utils.block_new.hash_block()
                    Utils.block_chain_have_sync.append(Utils.block_new)
                    Utils.ResponseNumber['syncCommit'] = 0
                    print('Well: we have Sync block')

                    # send add request
                    for i in Utils.node:
                        Utils.send_message_to_all(url='http://%s/block/sync/add' % i.address,
                                                  method='POST',
                                                  data_map={
                                                      'local_address': Utils.main_node.address,
                                                      'hash': response_hash,
                                                      response_hash: json.dumps(obj=Utils.block_new,
                                                                                default=Utils.parse_block),
                                                      'aim_address': aim_address,
                                                  })
                    Utils.create_new_block()

                # all response have received!
                if node_count <= Utils.ResponseNumber[response_hash + 'prepare']:
                    if permit_count < node_count // 2:
                        # sync fail
                        Utils.SyncFlag = False
                        Utils.create_new_block()
                        Utils.ChainFlag['sync_flag'] = False
                        print('Fail: we cannot Sync block')

                    Utils.RequestFlag.pop(response_hash + 'prepare')
                    Utils.ResponseNumber.pop(response_hash + 'prepare')
                    for i in Utils.SignMap[response_hash + 'prepare']:
                        Utils.ResponseResult.pop(i)
                    Utils.SignMap.pop(response_hash + 'prepare')

            # this address is't aim, so redirect this request
            else:
                for i in Utils.node:
                    if i.address != local_address:
                        Utils.send_message_to_all(url='http://%s/node/response/sync/prepare'
                                                      '?local_address=%s&aim_address=%s&result=%s&sign=%s&hash=%s'
                                                      % (i.address, Utils.main_node.address, aim_address,
                                                         result, Utils.get_node_sign(response_hash + 'prepare'),
                                                         response_hash))

        except BaseException as e:
            logging.exception(e)

    @coroutine
    def request_sync_commit(self):
        try:

            local_address = self.get_argument('local_address')
            aim_address = self.get_argument('aim_address')

            # aim address is the node
            if aim_address == Utils.main_node.address:
                Utils.ResponseNumber['syncCommit'] += 1
                if Utils.ResponseNumber['syncCommit'] >= len(Utils.NodeNumber.keys()):
                    Utils.ChainFlag['sync_flag'] = False
                    Utils.ResponseNumber.pop('syncCommit')

            # other node, redirect send
            else:
                for i in Utils.node:
                    if i.address == local_address:
                        continue
                    Utils.send_message_to_all(url='http://%s/node/request/sync/commit?aim_address=%s&local_address=%s'
                                              % (i.address, aim_address, Utils.main_node.address))

        except BaseException as e:
            logging.exception(e)

    @coroutine
    def request_sync_prepare(self):
        try:

            local_address = self.get_argument('local_address')
            aim_address = self.get_argument('aim_address')
            temp_hash = self.get_argument('hash')

            if Utils.SyncFlag:
                result = 'reject'
            else:
                Utils.SyncFlag = True
                result = 'permit'

            for i in Utils.node:
                if i.address == local_address:
                    Utils.send_message_to_all(url='http://%s/node/response/sync/prepare'
                                                  '?local_address=%s&aim_address=%s&result=%s&sign=%s&hash=%s'
                                              % (i.address, Utils.main_node.address, aim_address,
                                                 result, Utils.get_node_sign(temp_hash + 'prepare'), temp_hash))
                    continue
                Utils.send_message_to_all(url='http://%s/node/request/sync/prepare' % i.address,
                                          method='POST',
                                          data_map={
                                              'local_address': Utils.main_node.address,
                                              'aim_address': aim_address,
                                              'hash': temp_hash,
                                          })
        except BaseException as e:
            logging.exception(e)

    @coroutine
    def response_transaction_pre_prepare(self):

        try:

            local_address = self.get_argument('local_address')
            result = self.get_argument('result')
            aim_address = self.get_argument('aim_address')
            response_sign = self.get_argument('sign')
            response_hash = self.get_argument('hash')

            # this is node send this transaction
            if aim_address == Utils.main_node.address:

                Utils.SignMap[response_hash + 'pre_prepare'].append(response_sign)
                Utils.ResponseNumber[response_hash + 'pre_prepare'] += 1
                Utils.ResponseResult[response_sign] = result
                node_count = len(Utils.NodeNumber.keys())

                permit_count = Utils.get_count_from_map(result_map=Utils.ResponseResult,
                                                        key_list=Utils.SignMap[response_hash + 'pre_prepare'])
                # here is stand of request through verify!
                if permit_count > node_count // 2 and Utils.RequestFlag[response_hash + 'pre_prepare']:
                    Utils.RequestFlag[response_hash + 'pre_prepare'] = False
                    # send prepare request
                    Utils.RequestFlag[response_hash + 'prepare'] = True
                    Utils.ResponseNumber[response_hash + 'prepare'] = 0
                    Utils.SignMap[response_hash + 'prepare'] = []
                    for i in Utils.node:
                        Utils.send_message_to_all(url='http://%s/node/request/transaction/prepare?'
                                                      'local_address=%s&aim_address=%s&hash=%s'
                                                  % (i.address, Utils.main_node.address,
                                                     Utils.main_node.address, response_hash))

                # all response have received!
                if node_count <= Utils.ResponseNumber[response_hash + 'pre_prepare']:
                    if permit_count < node_count // 3:
                        transaction_temp = Utils.transaction_not_verify_cache[response_hash]
                        transaction_temp.status = transaction_temp.STATUS.FAIL
                        transaction_temp.hash = transaction_temp.transaction_hash()
                        Utils.transaction_have_verify_cache.append(transaction_temp)
                    Utils.RequestFlag.pop(response_hash + 'pre_prepare')
                    Utils.ResponseNumber.pop(response_hash + 'pre_prepare')
                    for i in Utils.SignMap[response_hash + 'pre_prepare']:
                        Utils.ResponseResult.pop(i)
                    Utils.SignMap.pop(response_hash + 'pre_prepare')

            # this address is't aim, so redirect this request
            else:
                for i in Utils.node:
                    if i.address != local_address:
                        Utils.send_message_to_all(url='http://%s/node/response/transaction/pre_prepare'
                                                      '?local_address=%s&result=%s&aim_address=%s'
                                                      '&hash=%s&sign=%s'
                                                      % (i.address, Utils.main_node.address, result,
                                                         aim_address, response_hash, response_sign))

        except BaseException as e:
            logging.exception(e)

    @coroutine
    def response_transaction_prepare(self):
        try:

            local_address = self.get_argument('local_address')
            result = self.get_argument('result')
            aim_address = self.get_argument('aim_address')
            response_sign = self.get_argument('sign')
            response_hash = self.get_argument('hash')

            # this is node send this transaction
            if aim_address == Utils.main_node.address:
                Utils.SignMap[response_hash + 'prepare'].append(response_sign)
                Utils.ResponseNumber[response_hash + 'prepare'] += 1
                Utils.ResponseResult[response_sign] = result
                node_count = len(Utils.NodeNumber.keys())
                permit_count = Utils.get_count_from_map(result_map=Utils.ResponseResult,
                                                        key_list=Utils.SignMap[response_hash + 'prepare'])
                # here is stand of request through verify!
                if permit_count > node_count // 3 and Utils.RequestFlag[response_hash + 'prepare']:
                    Utils.RequestFlag[response_hash + 'prepare'] = False
                    # send prepare request
                    for i in Utils.node:
                        Utils.send_message_to_all(url='http://%s/node/request/transaction/commit?'
                                                      'local_address=%s&hash=%s'
                                                  % (i.address, Utils.main_node.address, response_hash))

                # all response have received!
                if node_count <= len(Utils.SignMap[response_hash + 'prepare']):
                    if permit_count < node_count // 3:
                        transaction_temp = Utils.transaction_not_verify_cache[response_hash]
                        transaction_temp.status = transaction_temp.STATUS.FAIL
                        transaction_temp.hash = transaction_temp.transaction_hash()
                        Utils.transaction_have_verify_cache.append(transaction_temp)
                    Utils.RequestFlag.pop(response_hash + 'prepare')
                    Utils.ResponseNumber.pop(response_hash + 'prepare')
                    for i in Utils.SignMap[response_hash + 'prepare']:
                        Utils.ResponseResult.pop(i)
                    Utils.SignMap.pop(response_hash + 'prepare')

            # this address is't aim, so redirect this request
            else:
                for i in Utils.node:
                    if i.address != local_address:
                        Utils.send_message_to_all(url='http://%s/node/response/transaction/prepare'
                                                      '?local_address=%s&result=%s&aim_address=%s'
                                                      '&hash=%s&sign=%s'
                                                      % (i.address, Utils.main_node.address, result,
                                                         aim_address, response_hash, response_sign))

        except BaseException as e:
            logging.exception(e)

    @coroutine
    def request_transaction_prepare(self):
        try:

            local_address = self.get_argument('local_address')
            temp_hash = self.get_argument('hash')
            aim_address = self.get_argument('aim_address')

            result = 'permit'
            sign = Utils.get_node_sign(temp_hash + 'prepare')

            for i in Utils.node:
                if i.address == local_address:
                    Utils.send_message_to_all(url='http://%s/node/response/transaction/prepare'
                                                  '?local_address=%s&result=%s&aim_address=%s'
                                                  '&hash=%s&sign=%s'
                                                  % (i.address, Utils.main_node.address, result,
                                                     aim_address, temp_hash, sign))
                    continue
                Utils.send_message_to_all(url='http://%s/node/request/transaction/prepare?'
                                              'local_address=%s&aim_address=%s&hash=%s'
                                              % (i.address, Utils.main_node.address,
                                                 aim_address, temp_hash))

        except BaseException as e:
            logging.exception(e)

    @coroutine
    def request_transaction_commit(self):
        try:

            local_address = self.get_argument('local_address')
            temp_hash = self.get_argument('hash')

            for i in Utils.node:
                if i.address != local_address:
                    Utils.send_message_to_all(url='http://%s/node/request/transaction/commit?'
                                                  'local_address=%s&hash=%s'
                                                  % (i.address, Utils.main_node.address, temp_hash))

            # set transaction
            transaction_temp = json.loads(Utils.transaction_not_verify_cache[temp_hash],
                                          object_hook=Utils.load_transaction)
            transaction_temp.status = transaction_temp.SUCCESS
            transaction_temp.hash = transaction_temp.transaction_hash()
            Utils.transaction_have_verify_cache.append(json.dumps(obj=transaction_temp,
                                                                  default=Utils.parse_transaction))

        except BaseException as e:
            logging.exception(e)


# Account Handle
class AccountHandle(RequestHandler):

    def get(self, *args, **kwargs):
        if self.request.uri.startswith('/account/register'):
            self.register_account()
        elif self.request.uri.startswith('/account/connect'):
            self.user_connect()
        elif self.request.uri.startswith('/account/get'):
            self.user_get()
        elif self.request.uri.startswith('/account/gas/add'):
            self.gas_add()

    def post(self, *args, **kwargs):
        if self.request.uri.startswith('/account/add'):
            self.add_account()

    @coroutine
    def gas_add(self):
        try:

            address = self.get_argument('address')
            gas = int(self.get_argument('gas'))

            if gas <= 0:
                raise BaseException('Error: gas must be plus!')

            if isinstance(Utils.get_account(address, Utils.block_chain_have_sync[:]), str):
                raise BaseException('Error: your address is incorrect!')

            if address not in Utils.block_new.account_transaction:
                Utils.block_new.account_transaction.setdefault(address, [gas])
            else:
                Utils.block_new.account_transaction.get(address).append(gas)
            self.write('Success: %s\'s gas add success' % address)

        except BaseException as e:
            logging.exception(e)
            self.write(e.args[0])

    @coroutine
    def user_get(self):
        try:

            account_address = self.get_argument('address')
            # account = Utils.get_account(account_address, Utils.block_chain_have_sync[:])
            # self.write(json.dumps(account, default=Utils.parse_account))
            self.write(str(Utils.get_account_balance(account_address, block=Utils.block_chain_have_sync[:])[-1]))

        except BaseException as e:
            logging.exception(e)
            self.write('Error: you cannot get message, please check you address!')

    @coroutine
    def user_connect(self):
        try:
            user_address = self.get_argument('address')
            account_dir = self.get_arguments('dir')

            if account_dir:
                Account_Utils.init_environment(account_dir[0])
            else:
                if Account_Utils.init_environment().startswith('Error'):
                    raise BaseException('Error: your path is not exist or this path have used')

            account_address, private_pem = Account_Utils.load_account()

            if not account_address:
                raise BaseException('Error: you have no register!!')

            if user_address != account_address:
                raise BaseException('Error: you cannot connect chain use this address!!')

            account = Utils.get_account(user_address, Utils.block_chain_have_sync[:])

            if isinstance(account, str):
                raise BaseException('Error: your message is verifying, please waiting little!!')

            public_pem = account.signature

            if Account_Utils.verify_user(public_pem, private_pem):
                self.write('Success: you can connect!')
                return

            raise BaseException('Error: you private key is error!!!')

        except BaseException as e:
            logging.exception(e)
            self.write(e.args[0])

    @coroutine
    def add_account(self):
        try:

            address = self.get_argument('address')
            account = self.get_argument(address)
            local_address = self.get_argument('local_address')

            Utils.block_new.account[address] = account

            for i in Utils.node:
                if i.address == local_address:
                    continue
                Utils.send_message_to_all(url='http://%s/account/add' % i.address,
                                          method='POST',
                                          data_map={
                                              'local_address': Utils.main_node.address,
                                              'address': address,
                                              address: account,
                                          })
        except BaseException as e:
            logging.exception(e)

    @coroutine
    def register_account(self):
        try:

            account_name = self.get_argument('name')
            account_address = self.get_argument('address')
            account_data = self.get_argument('data')
            account_dir = self.get_arguments('dir')

            if account_dir:
                result = Account_Utils.init_environment(account_dir[0], register=True)
            else:
                result = Account_Utils.init_environment(register=True)
            if result.startswith('Error'):
                raise BaseException(result)

            private_pem, public_pem = Account_Utils.generate_keys()
            user_hash, account = Utils.register_account(account_name, account_address, account_data, public_pem)

            Account_Utils.save_account(account_address, private_pem)
            for i in Utils.node:
                Utils.send_message_to_all(url='http://%s/account/add' % i.address,
                                          method='POST',
                                          data_map={
                                              'local_address': Utils.main_node.address,
                                              'address': account_address,
                                              account_address: account,
                                          })

            self.write('Success: your account register successful, and your hash is ' + user_hash)
        except BaseException as e:
            logging.exception(e)
            self.write(e.args[0])
