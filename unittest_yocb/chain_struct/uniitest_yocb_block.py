from yocb.chain_struct.Block import Block
import unittest
import root
import json


class BlockTest(unittest.TestCase):

    def test_genesis(self):
        file = root.get_root()
        block = Block.genesis(file + '/genesis.json')
        print(block.__dict__)
        self.assertEqual(block.version, "#version1", "Error")

    def test_new_block(self):
        b = Block()
        block = Block.generate_block(b)
        return block

    def test_json(self):
        file = root.get_root() + '/genesis.json'
        block = Block()
        print(file)
        with open(file, 'w') as f:
            json.dump(fp=f, obj=block, default=Block.json_parse)

        with open(file, 'r') as f:
            temp = json.load(fp=f, object_hook=Block.json_load)
            print(temp.__dict__)

    def test_time(self):
        import datetime
        b = Block()
        b.timestamp = str(datetime.datetime.now())
        time = "2018-07-16 17:00:00"
        result = b.compare_block(time)
        self.assertEqual(result, False)


if __name__ == '__main__':
    unittest.main()
