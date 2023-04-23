import asyncio
import logging
import struct
import messages.packet as packet
import random
import time

logger = logging.getLogger(__name__)

class Receiver:
    async def receive_data(self, message):
        # current time - assumes synchronized clocks
        timestamp = int(time.time_ns() / 1000.0)
        # compute the packet latency
        latency = timestamp - message.timestamp

        print(latency)

    async def receive_message(self, message):
        if message.packet_type == packet.PacketType.DATA:
            await self.receive_data(message)
            return True
        elif message.packet_type == packet.PacketType.CONTROL_END:
            logger.warn('receive_message(): CONTROL_END')
            return False
        elif message.packet_type == packet.PacketType.CONTROL_START:
            logger.warn('receive_message(): CONTROL_START')
            return True
        
    def decode_next(self, ibuffer: bytearray, addr):
        if len(ibuffer) != 0:
            pkt_type = packet.PacketType(ibuffer[0])
            logger.debug(f'decode_next(): {pkt_type}')
            if pkt_type in (packet.PacketType.CONTROL_END, packet.PacketType.CONTROL_START):
                del ibuffer[0]
                message = packet.Packet(pkt_type, addr)
                logger.debug(f'decode_next(): {message}')
                return message
            elif len(ibuffer) < 3:
                # not enough bytes to unpack the length
                logger.debug('decode_next(): not enough to decode length')
                return None
            else:
                (length,) = struct.unpack('!H', ibuffer[1:3])
                logger.debug(f'decode_next(): length = {length}')
                # are there enough bytes to unpack the contents?
                if len(ibuffer) < (length + 3):
                    logger.debug('decode_next(): not enough data in buffer')
                    return None
                # read the packet contents
                # unpack the payload
                payload = ibuffer[3:(3 + length)]
                (
                    seq_no,
                    timestamp,
                    price,
                    quantity,
                    symbol
                ) = struct.unpack("!IQdIs", payload)

                logger.debug(f'decode_next(): data-message: length = {length}')
                del ibuffer[0:(3 + length)]
                message = packet.DataPacket(addr, seq_no, timestamp, price, quantity, symbol)
                return message
        
        return None