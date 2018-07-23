from tornado.web import RequestHandler
from tornado.gen import coroutine
import json
from yocb.tools import BlockTools, Tool
from yocb.chain_struct.Block import Block


_variable = Tool.get_variable()


class BlockHandle(RequestHandler):

    uri = None
    _variable = Tool.get_variable()

    def prepare(self):
        uri = self.request.uri
        self.uri = '?' in uri and uri[:uri.index('?')] or uri

    def get(self, *args, **kwargs):

        if self.uri.startswith('/block/get'):
            self.block_get()
        elif self.uri.startswith('/block/sync'):
            self.synchronized()

    # get block, if your index out of range, return error message,
    # if no specify index, return new 100 block
    # if all block is not enough, return all.
    @coroutine
    def block_get(self):

        result = 'Error: your index out of range!'
        sync_block = self._variable.get('synchronized_block')
        if self.get_arguments('index'):
            index = int(self.get_argument('index'))
            if sync_block[-1].index >= index:
                result = json.dumps(obj=sync_block[index], default=Block.json_parse)
        else:
            result = json.dumps([json.dumps(obj=i, default=Block.json_parse) for i in sync_block])
        self.write(result)

    # synchronized block chain in all network on generate block,
    # the connection is only requested by node,
    # user cannot assess.
    @coroutine
    def synchronized(self):
        if self.request.host not in _variable['agent_nodes']:
            self.write('Error: your computer is bad, please download a software in yun.com/2!')
            return
        block = self.get_argument('block')
        md5 = self.get_argument('md5')
        if Tool.generate_md5(block) != md5:
            # the block is invalid, maybe reason is network, and the block is destroy.
            # so we need obtain the block again.
            pass
        block = json.loads(block, object_hooks=Block.json_load)
        if block.pre_block_hash != _variable['synchronized_block'][-1].hash:
            # we miss some block, so we should obtain all miss block
            pass
        BlockTools.append_synchronized_block(block)
