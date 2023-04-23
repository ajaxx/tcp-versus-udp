import hashlib
import logging
import logging.handlers
import selectors
import socket
import uuid

import packet
import trade

logger = logging.getLogger(__name__)

class UDP_Proxy:
    def __init__(self, id):
        self.id = id

class UDP_Server:
    def __init__(self, selector, receiver):
        self.id = str(uuid.uuid4())
        self.receiver = receiver
        self.selector = selectors.DefaultSelector() if selector is None else selector
        self.socket = None

    async def bind(self, port):
        host = ''
        # create the socket (for communication)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        # set the socket timeout so that we do not block indefinitely
        self.socket.settimeout(1.0)
        logger.debug(f'bind(): host = {host}, port = {port}')
        self.selector.register(self.socket, selectors.EVENT_READ, self.receive)

    def receive_data(self, packet_data, sender):
        try:
            tr = trade.decode(packet_data)
        except Exception as e:
            logger.warning('receive_data(): failed to decode', exc_info = e)
            self.receiver.decode_failure()
            return

        self.receiver.receive_trade(sender, tr)

    def receive_datagram(self, datagram, sender):
        (packet_type, packet_data, packet_crc, packet_error) = packet.unpack(datagram)
        if packet_error:
            logger.error('receive_datagram(): packet error detected')
        elif packet_type == packet.PacketType.DATA:
            self.receive_data(packet_data, sender)
        elif packet_type in (packet.PacketType.CONTROL_START, packet.PacketType.CONTROL_END):
            pass
        else:
            logger.error(f'unrecognized datagram: {packet_type}')

    async def receive(self, sock):
        logger.debug(f'receive(): sock = {sock}')

        try:
            # receive the raw wire message
            (data, addr) = sock.recvfrom(4096)
            # receive the datagram
            self.receive_datagram(data, UDP_Proxy(f'{addr[0]}:{addr[1]}'))
        except socket.timeout:
            pass
