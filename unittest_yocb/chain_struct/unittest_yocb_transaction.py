import unittest
from yocb.chain_struct.Transaction import Transaction
import json
from datetime import datetime
from yocb.chain_struct.Block import Block
import root


class TransactionTest(unittest.TestCase):

    @unittest.skip(u'skip')
    def test_json(self):
        transaction = Transaction()
        print(transaction.__dict__)
        parse_json = json.dumps(obj=transaction, default=Transaction.json_parse)
        print(parse_json)
        load_json = json.loads(parse_json, object_hook=Transaction.json_load)
        self.assertEqual(load_json.status, 'Verifying', 'Er')

    @unittest.skip('skip')
    def test_generate(self):
        transaction = Transaction.generate_transaction(str(datetime.now()), "{dd:f}", 5, 2, 1)
        print(transaction.__dict__)
        self.assertEqual(transaction.gas, 5)

    def test_obtain(self):
        transaction = Transaction.generate_transaction(str(datetime.now()), "{dd:f}", 5, 2, 1)
        print(transaction.hash)
        block = Block.generate_block(Block.genesis(root.get_root() + '/genesis.json'))
        block.transactions.setdefault(transaction.hash, json.dumps(obj=transaction, default=Transaction.json_parse))
        status, output = Transaction.obtain_transaction('', block)
        self.assertEqual(status, 400)
        print(output)
        status, output = Transaction.obtain_transaction(transaction.hash, block)
        self.assertEqual(status, 200)
        print(output)
        status, output = Transaction.obtain_transaction('562140165816165', block)
        self.assertEqual(status, 400)
        print(output)


if __name__ == '__main__':
    unittest.main()
