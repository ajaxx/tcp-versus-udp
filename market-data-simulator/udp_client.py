import asyncio
import logging
import logging.handlers
import argparse
import socket
import packet
import streamer
import trade

logger = logging.getLogger(__name__)

class UDP_Client:
    def __init__(self):
        self.sock = None

    async def connect(self, host, port):
        self.count = 0
        self.dst_addr = socket.gethostbyname(host)
        self.dst_port = port
        # create the socket (for communication)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind the local address (random port) for return messages
        self.sock.bind(('', 0))
        # set the socket timeout so that we do not block indefinitely
        self.sock.settimeout(1.0)

    def send_message(self, message: bytes):
        self.sock.sendto(message, (self.dst_addr, self.dst_port))

    def send_trade(self, t: trade.Trade):
        # encode the trade
        message = t.encode()
        # message framing
        message = packet.data(message)
        # send the message
        self.send_message(message)
        # information for the logs        
        if ((t.seq_no % 10000) == 0):
            logger.debug(f'send_trade(): {t.seq_no}')
        self.count += 1

    async def close(self):
        print('close')
        self.sock.close()
        self.sock = None
