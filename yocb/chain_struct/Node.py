import hashlib
import requests


class Node(object):

    def __init__(self):
        self.address = None
        self.description = None
        self.timestamp = None
        self.status = None
        self.agent_nodes_count = 1
        self.child_nodes_count = 0
        self.pre_node_address = None
        self.child_nodes_address = []
        # generate block mark, True or False
        self.generate_mark = True
        # computer power mark, True or False
        self.com_pow_mark = True
        self.hash = None

    # create local hash
    def node_hash(self):
        sha = hashlib.sha256()
        sha.update((
            str(self.address) +
            str(self.description) +
            str(self.timestamp) +
            str(self.status) +
            str(self.pre_node_address) +
            str(self.generate_mark) +
            str(self.com_pow_mark)
                   ).encode())
        return sha.hexdigest()

    # register a user, and in here, we only offer address, description, timestamp, status
    # then we will set other value at out.
    @staticmethod
    def generate_local_node(address, description, timestamp):
        node = Node()
        node.address = address
        node.description = description
        node.timestamp = timestamp
        return node

    # destroy a node, because that is bad(after detect fail). we need note's address
    @staticmethod
    def destroy(node, address, node_group, node_type='child'):
        if node_type.startswith('child'):
            if address not in node.child_nodes_address:
                return 201, "Error: the event can't be disposed in here, you should send it to other node!"
            node.child_nodes_address.remove(address)
            node.child_nodes_count -= 1
            node_group[node.address].remove(address)
            return 200, 'Success: destroy ok!'
        elif node_type.startswith('agent'):
            node.agent_nodes_count -= 1
            node_group.remove(address)
            return 200, 'Success: destroy ok!'
        return 400, 'Error: your type of node is invalid!'

    # detect a node. return true or false
    @staticmethod
    def detect(address):
        try:
            for i in range(3):
                response = requests.get(address, timeout=2)
                if response.status_code != 200 and i == 2:
                    raise BaseException('Error: the node is bad!')
            # other detect
            return 200, 'Success: the node can be trusted!'
        except BaseException as e:
            return 400, str(e.args[0]).find('Connection refused') and 'Error: the node can\'t be connected!'
