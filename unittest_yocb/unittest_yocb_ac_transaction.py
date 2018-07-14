import unittest
from yocb.AcTransaction import AcTransaction
from datetime import datetime
from yocb.Block import Block
import json


class AcTest(unittest.TestCase):

    @unittest.skip('skip')
    def test_json(self):
        ac_transaction = AcTransaction.append_ac_transaction('0x121', str(datetime.now()), None, None, None, 5)
        self.assertEqual(ac_transaction.address, '0x121')
        p = json.dumps(obj=ac_transaction, default=AcTransaction.json_parse)
        print(p)
        l = json.loads(p, object_hook=AcTransaction.json_load)
        self.assertEqual(l.address, '0x121')
        print(l.__dict__)

    def test_obtain(self):
        ac_transaction = AcTransaction.append_ac_transaction('0x121', str(datetime.now()), None, None, None, 5)
        b = Block()
        b.ac_transactions.setdefault(ac_transaction.address,
                                     {ac_transaction.hash: json.dumps(ac_transaction, default=AcTransaction.json_parse)})
        status, output = AcTransaction.obtain_ac_transaction(ac_transaction.address, ac_transaction.hash, b)
        self.assertEqual(status, 200)
        print(output)


if __name__ == '__main__':
    unittest.main()
