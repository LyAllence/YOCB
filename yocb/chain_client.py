import threading
from yocb.tools import Tool
from yocb.chain_struct.Block import Block
from datetime import datetime
import sys
import logging


_variable = Tool.get_variable()


def start():
    if _variable['local_node'].generate_mark:
        _variable['storage_block'].timestamp = str(datetime.now())
        _variable['storage_block'].synchronized = True
        _variable['storage_block'].hash = _variable['storage_block'].hash_block()
        _variable['synchronized_block'].append(_variable['storage_block'])
        logging.info('generate block well, and the block hash is {}...'.format(_variable['storage_block'].hash))
        _variable['storage_block'] = Block.generate_block(_variable['synchronized_block'][-1])
        # update status on block

    threading.Timer(3, start).start()


def chain():
        threading.Timer(3, start).start()

