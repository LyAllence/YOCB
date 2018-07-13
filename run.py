from tornado import ioloop
from tornado.web import Application
from config import ip, port
from Tornado_Http.views import MainHandle, BlockHandle
from Tornado_Http.views import MinerHandle
from Tornado_Http.views import TransactionHandle
from Tornado_Http.views import NodeHandle
from Tornado_Http.views import AccountHandle
from Block_Chain.Chain.Utils import booting_block_chain
import os
from tornado.httpserver import HTTPServer

views_list = [
    (r'/', MainHandle),
    (r'/block/sync/prepare', BlockHandle),
    (r'/block/get', BlockHandle),
    (r'/block/sync/add', BlockHandle),
    (r'/miner', MinerHandle),
    (r'/transaction/get', TransactionHandle),
    (r'/transaction/submit', TransactionHandle),
    (r'/node/user/get', NodeHandle),
    (r'/node/user/register', NodeHandle),
    (r'/node/user/register/request', NodeHandle),
    (r'/node/user/register/response', NodeHandle),
    (r'/node/user/register/add', NodeHandle),
    (r'/node/request/sync/prepare', NodeHandle),
    (r'/node/request/sync/commit', NodeHandle),
    (r'/node/response/sync/prepare', NodeHandle),
    (r'/node/request/transaction/pre_prepare', NodeHandle),
    (r'/node/response/transaction/pre_prepare', NodeHandle),
    (r'/node/request/transaction/prepare', NodeHandle),
    (r'/node/response/transaction/prepare', NodeHandle),
    (r'/node/request/transaction/commit', NodeHandle),
    (r'/account/register', AccountHandle),
    (r'/account/add', AccountHandle),
    (r'/account/connect', AccountHandle),
    (r'/account/get', AccountHandle),
    (r'/account/gas/add', AccountHandle),
]

setting = {
    'debug': True,
    'static_path': os.path.join(os.path.abspath('.'), 'static'),
           }


# application.listen(address=ip, port=port)

if __name__ == '__main__':
    booting_block_chain()
    application = Application(views_list, **setting)
    http_server = HTTPServer(application)
    http_server.listen(address=ip, port=port)
    ioloop.IOLoop.instance().start()
