import hashlib
import json
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5 as Cipher_v1_5
from Crypto.PublicKey import RSA
import base64
import os


class Account(object):

    def __init__(self):
        self.name = None
        self.address = None
        self.public_key = None
        self.timestamp = None
        self.description = None
        self.balance = 0
        self.hash = None

    # create local hash
    def user_hash(self):
        sha = hashlib.sha256()
        sha.update((str(self.name) +
                    str(self.address) +
                    str(self.public_key) +
                    str(self.timestamp) +
                    str(self.description) +
                    str(self.balance)
                    ).encode())
        return sha.hexdigest()

    # parse a account, for add it on block
    @staticmethod
    def json_parse(account):
        return {
            'name': account.name,
            'address': account.address,
            'public_key': account.public_key,
            'timestamp': account.timestamp,
            'description': account.description,
            'balance': account.balance,
            'hash': account.hash,
        }

    # load a account
    @staticmethod
    def json_load(account_dict):
        account = Account()
        account.name = account_dict['name']
        account.address = account_dict['address']
        account.public_key = account_dict['public_key']
        account.timestamp = account_dict['timestamp']
        account.description = account_dict['description']
        account.balance = account_dict['balance']
        account.hash = account_dict['hash']
        return account

    # create a account, you need offer name, address, public, timestamp, description
    @staticmethod
    def generate_account(name, address, public_key, timestamp, description):
        account = Account()
        account.name = name
        account.address = address
        account.public_key = public_key
        account.timestamp = timestamp
        account.description = description
        account.balance = 0
        account.hash = account.user_hash()
        return account

    # obtain balance, you need offer address and block, be similar to transaction
    @staticmethod
    def obtain_balance(address, block):
        if not address:
            return 400, 'Error: your address\'s norm is not accepted!'
        if address in block.accounts:
                return 200, json.loads(block.accounts.get(address), object_hook=Account.json_load).balance
        return 400, 'Error: the address is invalid, please check your hash!'

    # obtain message of account
    @staticmethod
    def obtain_account(address, block):
        if not address:
            return 400, 'Error: your address\'s norm is not accepted!'
        if address in block.accounts:
                return 200, block.accounts.get(address)
        return 400, 'Error: the address is invalid, please check your hash!'

    # generate keys
    @staticmethod
    def generate_keys():
        random_master = Random.new().read
        rsa_master = RSA.generate(1024, random_master)
        private_key = rsa_master.exportKey()
        public_key = rsa_master.publickey().exportKey()
        return private_key, public_key

    # encrypt a message use public key
    @staticmethod
    def encrypt_message(public_key, message):
        encrypt_rsa_key = RSA.importKey(public_key)
        encrypt_cipher = Cipher_v1_5.new(encrypt_rsa_key)
        return base64.b64encode(encrypt_cipher.encrypt(message.encode()))

    # decrypt message from ghost_private
    @staticmethod
    def decrypt_message(private_key, decrypt_text):
        random_generator = Random.new().read
        decrypt_rsa_key = RSA.importKey(private_key)
        decrypt_cipher = Cipher_v1_5.new(decrypt_rsa_key)
        return decrypt_cipher.decrypt(base64.b64decode(decrypt_text), random_generator).decode()

    @staticmethod
    # init environment , add path
    def init_environment(path, register, address):
        if not address:
            return 400, 'Error: your must specify your account address!'
        if not os.path.exists(path) or not os.path.isdir(path):
            return 400, 'Error: your path is not valid!'
        if register and os.path.exists(os.path.join(path, address + '.json')):
            return 400, 'Error: the address is exist, please update!'
        return 200, 'Error: your environment is well!'

    @staticmethod
    # save message to local account file
    # and the private is must decode
    def save_account(path, address, private_key):
        user_info = {
            'address': address,
            'private_key': private_key,
        }
        with open(os.path.join(path, address + '.json'), 'w') as account_file:
            json.dump(obj=user_info, fp=account_file)
        return 200, 'Success: save ok'

    @staticmethod
    # load local account file
    def load_account(path, address):
        if not os.path.join(path, 'account.json'):
            return 400, None, None
        try:
            with open(os.path.join(path, address + '.json'), 'r') as account_file:
                user_info = json.load(fp=account_file)
            return 200, user_info.get('address'), user_info.get('private_key')
        except BaseException as e:
            return 400, 'Error: file open error!', e.args[0]

    @staticmethod
    # verify user valid
    def verify_user(public_key, private_key, address):
        encrypt_text = Account.encrypt_message(public_key, address)
        decrypt_text = Account.decrypt_message(private_key, encrypt_text)
        return address == decrypt_text
