# this class represents a "trade"
# - it is the most common unit of exchange in our protocol

import logging
import random
import struct
import time

logger = logging.getLogger(__name__)

class Trade():
    def __init__(self, seq_no, timestamp, price, quantity, symbol):
        self.seq_no = seq_no
        self.timestamp = timestamp
        self.price = price
        self.quantity = quantity
        
        self.symbol = symbol
        if isinstance(self.symbol, str):
            self.symbol = self.symbol.encode()

        self.format = f"!IQdIH{len(symbol)}s"

    def __dict__(self):
        return {
            'seq_no' : self.seq_no,
            'timestamp' : self.timestamp,
            'price' : self.price,
            'quanitity' : self.quantity,
            'symbol' : self.symbol.decode()
        }
    
    def __repr__(self):
        return repr(self.__dict__())
    
    def encode(self):
        return struct.pack(
            self.format,
            self.seq_no,
            self.timestamp,
            self.price,
            self.quantity,
            len(self.symbol),
            self.symbol
        )

def decode(message):
    (seq_no, timestamp, price, quantity, length) = struct.unpack("!IQdIH", message[0:26])
    symbol = message[26:26 + length]

    if isinstance(symbol, (bytearray, bytes)):
        symbol = symbol.decode()

    return Trade(seq_no, timestamp, price, quantity, symbol)

def rand(symbol, sequence_no):
    # calculate the current timestamp
    timestamp = int(time.time_ns() / 1000.0)
    # generate a random price (will not affect encoded size)
    price = random.random()
    # generate a random quantity (will not affect encoded size)
    quantity = random.randint(100, 1000)
    # encode into the packet form
    return Trade(sequence_no, timestamp, price, quantity, symbol)

# this method returns a generator of trades
def stream(symbol, num_packets):
    for sequence_no in range(0, num_packets):
        yield rand(symbol, sequence_no)

    logger.info(f'stream(): terminating at {sequence_no}')