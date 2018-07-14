import unittest
from yocb.Node import Node
from datetime import datetime


class NodeTest(unittest.TestCase):

    @unittest.skip(u'skip')
    def test_register(self):
        node = Node.register('1', 'this is local node', str(datetime.now()), 'agent')
        print(node.__dict__)
        self.assertEqual(node.address, '1', 'Error')

    @unittest.skip(u'skip')
    def test_detect(self):
        status, output = Node.detect('http://18.18.117.118:12110')
        print(output)
        self.assertEqual(status, 400, 'E')

    def test_destroy(self):
        node_group = ['1']
        # node_group = {'2': ['1']}
        node = Node()
        node.child_nodes_address.append('1')
        node.child_nodes_count = 1
        node.address = '2'
        status, output = Node.destroy(node, '1', node_group, 'agent')
        print(output)
        print(node.__dict__)
        self.assertEqual(status, 200, 'e')
        # self.assertEqual(len(node_group.get('2')), 0, 't')
        self.assertEqual(len(node_group), 0, 't')


if __name__ == '__main__':
    unittest.main()

