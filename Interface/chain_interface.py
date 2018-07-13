import requests
from config import ip, port
import json


class ChainInterface(object):

    base_url = 'http://{}:{}/'.format(ip, port, )

    # send http request and get response
    @staticmethod
    def send_http(url, data=None, method='GET'):

        print(url)
        if method == 'GET':
            result = requests.get(url=url).text
        else:
            if data:
                result = requests.post(url=url, data=data).text
            else:
                result = requests.post(url=url).text
        return result

    # register account
    # parameters: name is user name
    #             address is account sign
    #             data is user info
    #             path is key directory
    # return: result of register
    # http: http://18.18.117.118:30000/account/register?name=Alice&data=midMing
    @staticmethod
    def account_register(username, address, data, path=None):

        if path:
            url = ChainInterface.base_url + 'account/register?name={}&address={}&data={}&dir={}'\
                .format(username, address, data, path)
        else:
            url = ChainInterface.base_url + 'account/register?name={}&address={}&data={}'\
                .format(username, address, data)
        return ChainInterface.send_http(url)

    # get account
    # parameters: account_address is account hash
    # return: account info or fail result
    # http: http://18.18.117.118:30000/account/get?hash=0
    @ staticmethod
    def account_get(account_address):

        url = ChainInterface.base_url + 'account/get?address={}'.format(account_address)
        return ChainInterface.send_http(url)

    # submit transaction
    # parameters: user_address is user address
    #             user_path is user key path
    #             data is transaction message
    #             gas is fee with user cost
    # return: result of submit transaction
    # http: url='http://18.18.117.118:30000/transaction/submit'
    @staticmethod
    def submit_transaction(user_address, message, gas, user_path=None):
        data = {}
        data.setdefault('address', user_address)
        user_path and data.setdefault('dir', user_path)
        data.setdefault('data', json.dumps(message))
        data.setdefault('gas', gas)
        url = ChainInterface.base_url + 'transaction/submit'
        return ChainInterface.send_http(url, data=data, method='POST')

    # get transaction
    # parameters: transaction_hash is transaction hash
    # return: transaction info or error message
    # http: http://18.18.117.118:30000/transaction/get?hash=0
    @staticmethod
    def get_transaction(transaction_hash):

        url = ChainInterface.base_url + 'transaction/get?hash={}'.format(transaction_hash)
        return ChainInterface.send_http(url)

    @staticmethod
    def add_gas(address, gas):

        url = ChainInterface.base_url + 'account/gas/add?address={}&gas={}'.format(address, gas)
        return ChainInterface.send_http(url)

    # override str
    def __str__(self):
        return " \
            'account_register': 'register account and parameter:(name, address, data, [path])', \n \
            'account_get': 'get account info and parameter: (account_address)', \n \
            'submit_transaction': 'submit transaction and parameter: (address, message, gas, user_path)', \n \
            'get_transaction': 'get transaction and parameter: transaction_hash', \n \
            'add_gas: add user gas and parameter: (address, gas)'} "


if __name__ == '__main__':

    C = ChainInterface()
    while True:
        print('1: register, 2: get account, 3: submit transaction, 4: get transaction, 5: add gas')
        res = input('Enter: ')
        if res == '1':
            print(C.account_register('Alice', '0123456', 'Alice_account'))
        if res == '2':
            print(C.account_get('0123456'))
        if res == '3':
            print(C.submit_transaction('0123456', {'Alice': 'TE RG'}, gas=5))
        if res == '4':
            print(C.get_transaction(input('Enter hash:')))
        if res == '5':
            print(C.add_gas('0123456', 2))
        if res == 'exit':
            break
