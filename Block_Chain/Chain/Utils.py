from Block_Chain.Define.Block import Block
from Block_Chain.Define.Transaction import Transaction
from Block_Chain.Define.Node import Node
from Block_Chain.Define.Account import Account
from datetime import datetime
from config import ip, port, transaction_limit, generate_time, gas_timeout
from hashlib import sha256
import json
import os
import threading
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from DB.FileDB import insert_into_file, get_last_file
import logging
import requests
from urllib.parse import urlencode
import zipfile
import datetime as det

base_path = os.path.abspath('.')
log_path = os.path.join(base_path, 'Log')
log_file_name = 'server_error.log'

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handle = logging.FileHandler(os.path.join(log_path, log_file_name))
handle.setLevel(level=logging.INFO)
logger.addHandler(handle)

block_chain_have_sync = []
node = []
block_new = None
transaction_not_verify_cache = {}
transaction_have_verify_cache = []
main_node = None
# storage chain flag
ChainFlag = {}
# statistics request(things) state(false or true)
RequestFlag = {}
# storage response result
ResponseResult = {}
# storage response number
ResponseNumber = {}
# storage sign
SignMap = {}
# storage node number
NodeNumber = {}
# storage block sync
SyncFlag = False
ChainFlag.setdefault('miner_flag', False)
ChainFlag.setdefault('sync_flag', False)


# register Account
def register_account(account_name, account_address, account_data, public_pem):
    account_temp = Account(account_name, account_address, str(datetime.now()), account_data)
    account_temp.signature = public_pem
    account_temp.hash = account_temp.user_hash()
    account = json.dumps(obj=account_temp, default=parse_account)
    block_new.account[account_address] = account
    return account_temp.hash, account


# get account balance
def get_account(user_address, block):
    history_number = len(block) - 1
    while history_number >= 0:
        if block[history_number].account and user_address in block[history_number].account:
            return json.loads(block[history_number].account[user_address], object_hook=load_account)
        history_number -= 1
    if block[0].index == 0:
        return 'Error: your address is invalid!'
    else:
        file_path = os.path.join(base_path, "temp" + os.sep + str(block[0].index - 1))
        if not os.path.exists(file_path):
            return 'Error: history data file error, maybe somebody delete it!!'
        with open(file_path, 'r') as file_load:
            block_load = json.load(fp=file_load)
        list_block = load_all_block(block_load)
        del block_load
        return get_account(user_address, list_block[:])


# register node
def register_node(address, data, hash_temp):
    node_address = [i.address for i in node]
    if address in node_address:
        return 'Error: you have registered in this block chain!!'
    timestamp = str(datetime.now())
    node_register = Node(address, data, timestamp)
    node_register.status = node_register.REPLICAS
    node_register.hash = hash_temp
    node.append(node_register)
    return node_register.hash


# get node
def get_node():
    return json.dumps([json.dumps(obj=node_per, default=parse_node) for node_per in node])


# parse a node to str
def parse_node(node_per):
    return {
        'address': node_per.address,
        'timestamp': node_per.timestamp,
        'data': node_per.data,
        'status': node_per.status,
        'hash': node_per.hash
    }


# create genesis block
def create_genesis_block():
    index = 0
    data = 'Genesis Block: this block will confirm your data file and your parameters, ' \
           'if invalid, we will warn you and quit your running!'
    previous_hash = None
    block = Block(index, data, previous_hash)
    block.timestamp = str(datetime.now())
    block.have_sync = True
    block.hash = block.hash_block()
    block_chain_have_sync.append(block)
    parse_block_to_file(new_block=block_chain_have_sync, file_name="genesis", block_size=1)


# create new block and this block is not sync
def create_new_block():
    block_last = block_chain_have_sync[-1]
    index = block_last.index + 1
    timestamp = str(datetime.now())
    data = "this is %s block, the block is created by chain at %s" % (index, timestamp)
    previous_hash = block_last.hash
    global block_new
    block_new = Block(index, data, previous_hash)
    block_new.timestamp = timestamp


# submit a transaction in transaction cache
def prepare_transaction(data, gas_price):
    data = json.dumps(data)
    timestamp = str(datetime.now())
    transaction = Transaction(timestamp, data, gas_price)
    transaction.status = transaction.VERIFY
    transaction_not_verify_cache[transaction.hash] = transaction
    return transaction.hash


# parse a block and return a map
def parse_block(block_one):
    map_parse_block = {
            'index': block_one.index,
            'timestamp': block_one.timestamp,
            'data': block_one.data,
            'previous_hash': block_one.previous_hash,
            'transaction': block_one.transaction,
            'contract_data': json.dumps(block_one.contract_data),
            'gas_limit': block_one.gas_limit,
            'block_size': block_one.block_size,
            'have_sync': block_one.have_sync,
            'account': json.dumps(block_one.account),
            'account_transaction': json.dumps(block_one.account_transaction),
            'hash': block_one.hash,
            }
    return map_parse_block


# parse a map and return a block
def load_block(block_dict):
    b = Block(None, None, None)
    b.index = block_dict['index']
    b.timestamp = block_dict['timestamp']
    b.data = block_dict['data']
    b.previous_hash = block_dict['previous_hash']
    b.gas_limit = block_dict['gas_limit']
    b.block_size = block_dict['block_size']
    b.hash = block_dict['hash']
    b.have_sync = block_dict['have_sync']
    b.contract_data = json.loads(block_dict['contract_data'])
    b.transaction = block_dict['transaction']
    b.account = json.loads(block_dict['account'])
    b.account_transaction = json.loads('account_transaction')
    return b


# parse account to map
def parse_account(account_one):
    return {
        'name': account_one.name,
        'address': account_one.address,
        'signature': account_one.signature,
        'timestamp': account_one.timestamp,
        'data': account_one.data,
        'balance': account_one.balance,
        'hash': account_one.hash,
    }


# load a map to account
def load_account(account_dict):
    account = Account(None, None, None, None)
    account.name = account_dict['name']
    account.signature = account_dict['signature']
    account.data = account_dict['data']
    account.timestamp = account_dict['timestamp']
    account.balance = account_dict['balance']
    account.hash = account_dict['hash']
    account.address = account_dict['address']
    return account


# parse a transaction and return a map
def parse_transaction(tran_one):
    return {
        "timestamp": tran_one.timestamp,
        'data': tran_one.data,
        'gas_price': tran_one.gas_price,
        'status': tran_one.status,
        'hash': tran_one.hash,
    }


# parse a map and return a transaction
def load_transaction(tran_dict):
    temp = Transaction(None, None, None)
    temp.timestamp = tran_dict['timestamp']
    temp.data = tran_dict['data']
    temp.gas_price = tran_dict['gas_price']
    temp.hash = tran_dict['hash']
    temp.status = tran_dict['status']
    return temp


# send message to all node in this net
def send_message_to_all(url=None, data_map=None, method='GET'):

    print(url)

    http_client = AsyncHTTPClient()
    if method == 'GET':
        http_request = HTTPRequest(method='GET', url=url)
    else:
        http_request = HTTPRequest(method='POST', url=url + '?' + urlencode(data_map), body='Alice')
    http_client.fetch(http_request)


# get genesis hash
def get_genesis_hash():
    with open(os.path.join(base_path, "temp/" + os.sep + 'genesis'), 'r') as file_load:
        genesis_block = json.loads(json.load(fp=file_load)[0], object_hook=load_block)
    return genesis_block.hash


# parse all block, and be purpose to storage or send to other node
def parse_all_block(block_sync_list):
    return [json.dumps(obj=block_per, default=parse_block) for block_per in block_sync_list]


# parse dicts to block_chain
def load_all_block(block_list):
    return [json.loads(block_per, object_hook=load_block) for block_per in block_list]


# storage block_chain on disk
def parse_block_to_file(new_block, file_name, block_size):
    block_list_to_file = parse_all_block(block_sync_list=new_block[:block_size])
    with open(os.path.join(base_path, "temp" + os.sep + file_name), 'w') as file_dump:
        json.dump(obj=block_list_to_file, fp=file_dump)
    global block_chain_have_sync
    if block_size == 1:
        insert_into_file(name=file_name, last_block_index=block_chain_have_sync[0].index)
    else:
        insert_into_file(name=file_name, last_block_index=block_chain_have_sync[block_size - 1].index)
        block_chain_have_sync = block_chain_have_sync[block_size:]


# get online block
def get_have_sync_block():
    return json.dumps(parse_all_block(block_chain_have_sync))


# boot block_chain with history file.
def start_chain_block(file_history_name):
    # load or create genesis block and create new block
    global main_node
    main_node = Node(address=ip + ':' + str(port),
                     data='this_is_node_of_%s' % ip + ":" + str(port),
                     timestamp=str(datetime.now()))
    main_node.status = main_node.REPLICAS
    main_node.hash = main_node.node_hash()
    if file_history_name:
        with open(os.path.join(base_path,  "temp/" + os.sep + file_history_name), 'r') as file_load:
            block_load = json.load(fp=file_load)
        block_list_all = load_all_block(block_load)
        global block_chain_have_sync
        block_chain_have_sync = block_list_all[:]
        del block_load
        del block_list_all
        create_new_block()

    else:
        create_genesis_block()
        create_new_block()


# get count of result in map
def get_count_from_map(key_list, result_map, result='permit'):
    count = 0
    for i in key_list:
        if result_map[i] == result:
            count += 1
    return count


# compare time, if in range return True, or False
# time_now is now time, is datetime. old time is block time, is str
def compare_time(time_setting, old_time):
    old_time = old_time[:old_time.rindex('.')]
    dat = datetime.strptime(old_time, '%Y-%m-%d %H:%M:%S')
    return time_setting <= dat


def get_list_index_gas(address, list_tran):
    index = 0
    gas = 0
    for i in list_tran:
        data = json.loads(i.data)
        if data.get('user_address') == address:
            if data.get('index') > index:
                index = data.get('index')
                gas = 0
        if data.get('index') == index:
            gas += data.get('use_gas')
    return index, gas


# get account balance with calculate user gas(add or cost in fixed times)
# return: index, gas, balance
def get_account_balance(address, block=None):

    range_list = get_range_block(block[:])
    index = 0
    gas = 0
    if address in transaction_not_verify_cache:
        index, gas = get_list_index_gas(address, transaction_not_verify_cache.get(address))

    if index == 0:
        index, gas = get_list_index_gas(address,
                                        [json.loads(tran_temp, object_hook=load_transaction)
                                         for tran_temp in transaction_have_verify_cache])

    if index == 0:
        for block_temp in range_list:
            index, gas = get_list_index_gas(address,
                                            [json.loads(tran_temp, object_hook=load_transaction)
                                             for tran_temp in block_temp.transaction])
            if index > 0:
                break

    balance = 0
    for block_temp in range_list:
        if address in block_temp.account_transaction:
            balance += sum(block_temp.account_transaction.get(address))
        if block_temp.index <= index:
            balance -= gas
            break
    return index, gas, balance


# return block list in range
def get_range_block(block, range_list_temp=None, time_setting=None):
    if not range_list_temp:
        range_list_temp = []
    if not time_setting:
        now_time = datetime.now()
        time_setting = now_time + det.timedelta(seconds=-gas_timeout)
    history_number = len(block) - 1
    while history_number >= 0:
        # get gas
        block_temp = block[history_number]
        if not compare_time(time_setting, block_temp.timestamp):
            return range_list_temp
        range_list_temp.append(block_temp)
        history_number -= 1

    if block[0].index == 0:
        return range_list_temp
    else:
        file_path = os.path.join(base_path, "temp" + os.sep + str(block[0].index - 1))
        with open(file_path, 'r') as file_load:
            block_load = json.load(fp=file_load)
        list_block = load_all_block(block_load)
        del block_load
        return get_range_block(list_block[:], range_list_temp, time_setting)


# return index and gas
def get_index_gas(address, block, index, gas, gas_price):

    range_list = get_range_block(block)
    range_list.reverse()
    for block_temp in range_list:
        balance = 0
        if address in block_temp.account_transaction:
            balance = sum(block_temp.account_transaction.get(address))
        if block_temp.index == index:
            balance -= gas
        if balance - gas_price >= 0:
            return block_temp.index, gas_price
        gas_price = gas_price - balance


# inspect hash is exists in block
def compare_hash(hash_com, block_hash):
    for i in block_hash.transaction:
        transaction = json.loads(i, object_hook=load_transaction)
        if transaction.hash == hash_com:
            return transaction
    return None


# submit a transaction
def user_submit_transaction(data, gas):
    transaction_temp = Transaction(timestamp=str(datetime.now()), data=data, gas_price=gas)
    transaction_temp.status = transaction_temp.VERIFY
    transaction_temp.hash = transaction_temp.transaction_hash()
    transaction_temp_parse = json.dumps(obj=transaction_temp, default=parse_transaction)
    if len(node) == 0:
        transaction_have_verify_cache.append(transaction_temp_parse)
    else:
        transaction_not_verify_cache[transaction_temp.hash] = transaction_temp_parse
    return transaction_temp.hash


# get a transaction message base from hash
def get_transaction(get_hash, block):
    history_number = len(block) - 1
    while history_number >= 0 and not compare_hash(get_hash, block[history_number]):
        history_number -= 1
    if history_number >= 0:
        return json.dumps(obj=compare_hash(get_hash, block[history_number]), default=parse_transaction)
    if block[0].index == 0:
        return 'Error: your transaction hash is invalid!!'
    else:
        file_path = os.path.join(base_path, "temp" + os.sep + str(block[0].index - 1))
        if not os.path.exists(file_path):
            return 'Error: history data file error, maybe somebody delete it!!'
        with open(file_path, 'r') as file_load:
            block_load = json.load(fp=file_load)
        list_block = load_all_block(block_load)
        del block_load
        return get_transaction(get_hash=get_hash, block=list_block[:])


# miner method
def miner_continue():
    if not ChainFlag['sync_flag']:
        block_new.timestamp = str(datetime.now())
        size = transaction_limit
        if len(transaction_have_verify_cache) < transaction_limit:
            size = len(transaction_have_verify_cache)
        block_new.transaction.extend(transaction_have_verify_cache[:size])
        block_new.hash = block_new.hash_block()
        for i in range(size):
            transaction_have_verify_cache.pop(0)
        # tran_temp = json.loads(transaction_have_verify_cache.pop(0), object_hook=load_transaction)
        #     data = json.loads(tran_temp.data)
        #     if data.get('user_address') not in block_new.account_transaction:
        #         block_new.account_transaction.setdefault(data.get('user_address'), [- tran_temp.gas_price])
        #     else:
        #         block_new.account_transaction.get(data.get('user_address')).append(- tran_temp.gas_price)
        ChainFlag['sync_flag'] = True
        if len(node) == 0:
            print("create new block !!")
            block_new.have_sync = True
            block_new.hash = block_new.hash_block()
            block_chain_have_sync.append(block_new)
            create_new_block()
            ChainFlag['sync_flag'] = False
        else:
            send_message_to_all(url='http://%s/block/sync/prepare' % main_node.address)
        threading.Timer(generate_time, miner_continue).start()


# when a node register, we will send it all block
def block_get_all():
    return json.dumps({
        'block_chain_have_sync': parse_all_block(block_sync_list=block_chain_have_sync),
        'address': node[0].address,
    })


# decompress a file
def unzip_file(file_path):
    try:
        with zipfile.ZipFile(file_path) as zip_file:
            zip_file.extractall(path='')
    except zipfile.BadZipFile as e:
        logging.info('Zip:', e)


# get data file from network
def get_data_from_http(address):
    url = "http://" + address + "/download/history_file"
    response = requests.request("GET", url, stream=True, data=None, headers=None)
    save_path = "data.zip"
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    unzip_file(save_path)


# get node sign
def get_node_sign(temp_hash):
    sha = sha256()
    sha.update((main_node.hash + temp_hash).encode())
    return sha.hexdigest()


# boot method
def booting_block_chain():
    filename = 'No File' or get_last_file()
    if 'No File' in filename:
        start_chain_block(file_history_name=None)
    else:
        start_chain_block(file_history_name=filename)
    threading.Timer(generate_time, miner_continue).start()
