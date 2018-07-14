from yocb.Block import Block
import unittest
import root
import json


class BlockTest(unittest.TestCase):

    # @unittest.skip(u'skip')
    def test_genesis(self):
        file = root.get_root()
        block = Block.genesis(file + '/genesis.json')
        print(block.__dict__)
        self.assertEqual(block.version, "#version1", "Error")

    @unittest.skip(u'skip')
    def test_new_block(self):
        b = Block()
        block = Block.generate_block(b)
        return block

    @unittest.skip(u'skip')
    def test_json(self):
        file = root.get_root() + '/genesis.json'
        block = Block()
        print(file)
        with open(file, 'w') as f:
            json.dump(fp=f, obj=block, default=Block.json_parse)

        with open(file, 'r') as f:
            temp = json.load(fp=f, object_hook=Block.json_load)
            print(temp.__dict__)


if __name__ == '__main__':
    unittest.main()
