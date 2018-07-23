import unittest
from yocb.tools import _variable
from yocb.tools import BlockTools
import root
import os
from yocb.tools import Block
from datetime import datetime


class BlockTest(unittest.TestCase):

    @unittest.skip('skip')
    def test_generate(self):
        BlockTools.genesis()
        BlockTools.generate_block(_variable['synchronized_block'][-1])
        print(_variable)

    def test_genesis(self):
        remote_file = ['{\n"index": 0,\n', '  "pre_block_hash": null,\n', '  "timestamp": null,\n', '  "version": "#version1",\n', '  "block_max_size": 5000,\n', '  "synchronized": false,\n', '  "accounts": "{}",\n', '  "transactions": "{}",\n', '  "ac_transactions": "{}",\n', '  "hash": null\n', '}']
        result = BlockTools.inspect_genesis(remote_file)
        self.assertEqual(result, True)


if __name__ == '__main__':
    unittest.main()

