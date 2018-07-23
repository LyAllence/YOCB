import unittest
from yocb.tools import Network


class NetworkTest(unittest.TestCase):

    def test_generate(self):
        status, output = Network.inspect_network('8.8.8.8')
        self.assertEqual(status, True)


if __name__ == '__main__':
    unittest.main()

