import asyncio
import logging
import logging.handlers
import argparse
import socket

import trade
import packet
import streamer

logger = logging.getLogger(__name__)

class TCP_Client:
    def __init__(self):
        self.count = 0
        self.sock = None

    async def connect(self, host, port):
        self.dst_addr = socket.gethostbyname(host)
        self.dst_port = port
        # create the socket (for communication)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.debug(f'connect(): host = {host}, port = {port}')
        self.sock.connect((host, port))
        # set the socket timeout so that we do not block indefinitely
        self.sock.settimeout(5.0)
        # set to blocking so that streaming occurs
        self.sock.setblocking(True)

    def send_message(self, message: bytes):
        # logger.debug(f'send(): length = {len(message)}')

        # send the message along
        sent_length = self.sock.send(message)
        
        # assume that the entire stream blocked until the message was
        # written to the stream - this is the normal behavior, but when
        # blocking is disabled, writes can be truncated
        assert(sent_length == len(message))

        #logger.debug(f'send(): length = {len(message)} => {sent_length}')

    def send_trade(self, t: trade.Trade):
        # encode the trade
        message = t.encode()
        # message framing
        message = packet.data(message)
        # send the message
        self.send_message(message)
        # information for the logs
        if ((t.seq_no % 10000) == 0):
            logger.info(f'send_trade(): {t.seq_no}')
        self.count += 1

    async def close(self):
        logger.info('close()')
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.sock = None
