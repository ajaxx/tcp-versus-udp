import asyncio
import collections
import logging
import logging.handlers
import socket
import selectors
import time
import uuid
import packet
import trade

logger = logging.getLogger(__name__)

class TCP_Instance:
    def __init__(self, sock, addr, selector, receiver):
        logger.debug(f'TCP_Instance(): sock = {sock}')
        self.id = str(uuid.uuid4())
        self.addr = addr
        self.selector = selector
        self.receiver = receiver
        self.buffer = bytearray()
    
    def receive_data(self, packet_data):
        try:
            tr = trade.decode(packet_data)
        except Exception as e:
            logger.warning('receive_data(): failed to decode', exc_info = e)
            self.receiver.decode_failure()
            return

        self.receiver.receive_trade(self, tr)

    def receive_packet(self, packet_type, packet_data):
        if packet_type == packet.PacketType.DATA:
            self.receive_data(packet_data)
        elif packet_type == packet.PacketType.CONTROL_START:
            logger.warning('control-start')
        elif packet_type == packet.PacketType.CONTROL_END:
            logger.warning('control-end')
            self.selector.stop()
        else:
            logger.warning(f'unknown packet received: {packet_type}')
    
    async def receive(self, sock: socket.socket):
        logger.debug(f'receive(): sock = {sock}')
        try:
            data = sock.recv(16384)
            if not data:
                logger.debug('receive(): unregistering socket')
                self.selector.unregister(sock)
                sock.close()
                return

            # add the data to the buffer, it may actually contain multiple packets
            self.buffer.extend(data)
            # unpack all packets in the stream
            for (packet_type, packet_data, packet_crc, packet_error) in packet.unpack_stream(self.buffer):
                self.receive_packet(packet_type, packet_data)
        except socket.timeout:
            print('timeout')
            pass

class TCP_Server:
    def __init__(self, selector, receiver):
        self.receiver = receiver
        self.selector = selector
        self.socket = None

    async def accept(self, sock):
        logger.debug(f'accept(): sock = {sock}')
        conn, addr = sock.accept()
        conn.setblocking(False)
        # create a wrapper
        wrapper = TCP_Instance(conn, addr, self.selector, self.receiver)
        # register with the selector
        self.selector.register(conn, selectors.EVENT_READ, wrapper.receive)
        return True

    async def bind(self, port):
        host = ''
        # create the socket (for communication)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.debug(f'bind(): host = {host}, port = {port}')
        sock.bind((host, port))
        sock.setblocking(False)
        # listen for connections
        sock.listen(100)
        # assign
        self.socket = sock
        self.selector.register(self.socket, selectors.EVENT_READ, self.accept)
