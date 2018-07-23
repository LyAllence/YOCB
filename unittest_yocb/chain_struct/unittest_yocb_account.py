import json
import unittest
from yocb.chain_struct.Account import Account
from datetime import datetime
from yocb.chain_struct.Block import Block
import root
import os


class TestAccount(unittest.TestCase):

    @unittest.skip('skip')
    def test_generate(self):
        account = Account.generate_account('TRG', '0x32', '323232', str(datetime.now()), "Agc")
        print(account.__dict__)
        self.assertEqual(account.name, 'TRG')

    @unittest.skip('skip')
    def test_json(self):
        account = Account.generate_account('TRG', '0x32', '323232', str(datetime.now()), "Agc")
        parse = json.dumps(obj=account, default=Account.json_parse)
        print(parse)
        ac = json.loads(parse, object_hook=Account.json_load)
        print(ac.__dict__)
        self.assertEqual(ac.name, 'TRG')

    @unittest.skip(u'skip')
    def test_obtain(self):
        address = '0x32'
        account = Account.generate_account('TRG', '0x32', '323232', str(datetime.now()), "Agc")
        block = Block.generate_block(Block.genesis(root.get_root() + '/genesis.json'))
        block.accounts.setdefault(address, json.dumps(obj=account, default=Account.json_parse))
        status, output = Account.obtain_balance(address, block)
        self.assertEqual(status, 200)
        print(output)
        self.assertEqual(output, 0)

    @unittest.skip(u'skip')
    def test_obtain_account(self):
        address = '0x32'
        account = Account.generate_account('TRG', '0x32', '323232', str(datetime.now()), "Agc")
        block = Block.generate_block(Block.genesis(root.get_root() + '/genesis.json'))
        block.accounts.setdefault(address, json.dumps(obj=account, default=Account.json_parse))
        status, output = Account.obtain_account(address, block)
        self.assertEqual(status, 200)
        print(output)

    @unittest.skip('skip')
    def test_keys(self):
        private_key, public_key = Account.generate_keys()
        encrypt_me = Account.encrypt_message(public_key, "have no risk!")
        print(encrypt_me)
        dec_me = Account.decrypt_message(private_key, encrypt_me)
        self.assertEqual(dec_me, 'have no risk!')

    @unittest.skip(u'skip')
    def test_verify_user(self):
        private_key, public_key = Account.generate_keys()
        bool = Account.verify_user(public_key, private_key, '0x121')
        self.assertEqual(bool, True)

    def test_load(self):
        path = os.path.abspath('.')
        status, output = Account.init_environment(path, True, '0x121')
        private_key, public_key = Account.generate_keys()
        print(output)
        self.assertEqual(status, 200)
        status, output = Account.save_account(path, '0x121', private_key.decode())
        print(output)
        self.assertEqual(status, 200)
        status, output, output1 = Account.load_account(path, '0x121')
        print(output, output1)
        self.assertEqual(status, 200)


if __name__ == '__main__':
    unittest.main()
