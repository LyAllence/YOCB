import logging
import root
import os
import sys
from tornado import ioloop
from tornado.web import Application
from tornado.httpserver import HTTPServer
from yocb.tools import Network, Logger, Tool
from yocb.tools import BlockTools
from handle.MainHandle import MainHandle
from handle.BlockHandle import BlockHandle
from yocb.chain_client import chain


views_list = [
    (r'/', MainHandle),
    (r'/block/get', BlockHandle),

]
settings = {
    'debug': True,
    'static_path': os.path.join(root.get_root(), 'static'),
}

if __name__ == '__main__':
    # inspect all environment
    Logger.info_logger()
    _variable = Tool.get_variable()

    # inspect network
    status, output = Network.inspect_network('8.8.8.8')
    if status != 0:
        logging.info('Fail <> Your network is ill, so you cannot join us!')
        sys.exit(1)
    logging.info('Success <> Network is ok...')

    # inspect datadir
    datadir = Tool.get_opt_number('-d') or Tool.get_opt_number('--datadir')
    if not datadir:
        logging.info('Fail <> you must set the datadir that the genesis.json\'s path!')
        exit(1)

    _variable['datadir'] = datadir

    logging.info('Datadir <> {}...'.format(_variable['datadir']))

    # set ip and port
    _variable['ip'] = Tool.get_opt_number('-i') or Tool.get_opt_number('--ip') or '0.0.0.0'
    _variable['port'] = Tool.get_opt_number('-p') or Tool.get_opt_number('--port') or 9527

    logging.info('Ip      <> {}...'.format(_variable['ip']))
    logging.info('Port    <> {}...'.format(_variable['port']))

    # inspect genesis.json
    BlockTools.genesis(_variable.get('datadir'))
    logging.info('Genesis <> load genesis ok...')

    # initial all variable
    Tool.init_variable()
    logging.info('Success <> local node initial well...')
    logging.info('Success <> storage block initial well...')
    logging.info('Initial <> all variable init all...')
    application = Application(views_list, **settings)
    http_server = HTTPServer(application)
    http_server.listen(address=_variable['ip'], port=_variable['port'])
    chain()
    logging.info('Start   <> threading running ok...')
    logging.info('Start   <> service is starting...')
    ioloop.IOLoop.instance().start()
