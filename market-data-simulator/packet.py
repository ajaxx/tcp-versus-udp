import struct

from enum import IntEnum
import zlib

class PacketType(IntEnum):
    CONTROL_START = 1
    CONTROL_END = 2
    DATA = 4

def unpack_stream(message_buffer: bytearray):
    message_len = len(message_buffer)
    while message_len >= 7:
        # remove the packet type
        # remove the packet length
        (packet_type, packet_crc, packet_len) = struct.unpack('!bIH', message_buffer[0:7])
        # convert the int to a packet type
        packet_type = PacketType(packet_type)
        # define the tail
        packet_tail = 7 + packet_len
        if message_len < packet_tail:
            return
        # extract the message data
        packet_data = message_buffer[7:packet_tail]
        # check the crc
        packet_crc_calc = zlib.crc32(packet_data)
        # remove the message data
        del message_buffer[0:packet_tail]
        message_len = len(message_buffer)
        # yield the data
        yield (packet_type, packet_data, packet_crc, packet_crc != packet_crc_calc)

def unpack(message_data):
    # minimum length is 7
    message_len = len(message_data)
    if message_len < 7:
        raise ValueError('invalid datagram received')
    # remove the packet type
    # remove the packet length
    (packet_type, packet_crc, packet_len) = struct.unpack('!bIH', message_data[0:7])
    # convert the int to a packet type
    packet_type = PacketType(packet_type)
    # remove the message data
    packet_data = message_data[7:7 + packet_len]
    # calculate the packet crc
    packet_crc_calc = zlib.crc32(packet_data)
    # return the packet data
    return (packet_type, packet_data, packet_crc, packet_crc != packet_crc_calc)

def pack(message_type: PacketType, message_data):
    message_crc = zlib.crc32(message_data)
    message_head = struct.pack('!bIH', int(message_type), message_crc, len(message_data))
    return (message_head + message_data)

def data(message_data):
    return pack(PacketType.DATA, message_data)

def start():
    return pack(PacketType.CONTROL_START, b'')

def end():
    return pack(PacketType.CONTROL_END, b'')