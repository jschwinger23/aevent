from . import aevent
from .aevent import monkey
monkey.patch_socket()

import os
import socket
from logging import getLogger

from ..common.server import Server

SLOW_ECHO_SERVER_PORT = os.environ.get('SLOW_ECHO_SERVER_PORT', 9000)
logger = getLogger(__name__)


class M4Server(Server):
    def serve_forever(self):
        while True:
            peer, addr = yield from self.sock.accept()
            aevent.spawn(self.handle_peer, peer, addr)

    def handle_peer(self, peer, addr):
        words = yield from peer.recv(1024)
        logger.info('M4 echo server recv %s from peer %s', words, addr)
        yield from peer.send((yield from self.request_slow(words)))
        yield from peer.close()

    def request_slow(self, text):
        logger.info('prepare to relay to slow echo server')
        req_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        yield from req_sock.connect(('', SLOW_ECHO_SERVER_PORT))
        yield from req_sock.send(text)
        return (yield from req_sock.recv(1024))


if __name__ == '__main__':
    m4_server = M4Server(8000)
    aevent.spawn(m4_server.serve_forever)
