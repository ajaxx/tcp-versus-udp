#!/usr/bin/python3

import argparse
import asyncio
import collections
import json
import logging
import logging.handlers
import threading
import time

import ipc_logging

from ipc_selector import IpcSelector
from udp_server import UDP_Server
from tcp_server import TCP_Server
from stats import StatisticsRepo, stat
from trade import Trade

logger = logging.getLogger(__name__)

class IpcReceiver():
    def __init__(self, data_file):
        self.data_file = data_file
        self.statistics = StatisticsRepo()
        self.decode_errors = 0
        self.separator = '\n'
        self.queue = collections.deque()
        self.event = threading.Event()

        if data_file is None:
            self.data_fd = None
        else:
            self.data_fd = open(data_file, 'w') 
            self.data_fd.write('[')

    def process_trade(self, sender, trade: Trade, time_recv):
        try:
            s = stat(trade, time_recv)
            s.insert(0, sender.id)
            # write to the data_fd
            if self.data_fd is not None:
                self.data_fd.write(self.separator + json.dumps(s))
            
            self.separator = ',\n'
        except Exception as e:
            logger.exception('failure to receive trade', exc_info = e)

    def process_queue(self):
        try:
            while True:
                try:
                    (sender, trade, time_recv) = self.queue.popleft()
                    self.process_trade(sender, trade, time_recv)
                except IndexError:
                    if self.event.is_set():
                        return
                    time.sleep(1.0)
        finally:
            if self.data_fd is not None:
                self.data_fd.write('\n]\n')
                self.data_fd.close()
                self.data_fd = None

    def start(self):
        self.thread = threading.Thread(target = self.process_queue, daemon = True)
        self.thread.start()

    def stop(self):
        self.event.set()

    def receive_trade(self, sender, trade: Trade):
        self.queue.append((sender, trade, int(time.time_ns() / 1000.0)))

class IpcEngine():
    def __init__(self, args):
        self.selector = IpcSelector()
        self.receiver = IpcReceiver(args.data_file)
        self.tcp_port = args.tcp_port
        self.udp_port = args.udp_port

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return self

    async def start_tcp(self):
        logger.info('start_tcp()')
        # we create the engine
        server = TCP_Server(self.selector, self.receiver)
        # bind the engine
        await server.bind(self.tcp_port)

    async def start_udp(self):
        logger.info('start_udp()')
        # we create the engine
        server = UDP_Server(self.selector, self.receiver)
        # bind the engine
        await server.bind(self.udp_port)
    
    async def start(self):
        self.receiver.start()
        await self.start_tcp()
        await self.start_udp()

    async def stop(self):
        self.receiver.stop()

    async def receive(self):
        logger.info('start_tcp()')
        await self.selector.receive()

# Parses command line arguments
def parseCmdLineArgs():
    parser = argparse.ArgumentParser(description="Reliable IPC Server")
    parser.add_argument("--debug", dest="log_level", action="store_const", const='debug', help="Log level set to debug")
    parser.add_argument("--log-level", dest="log_level", action="store", choices=['debug', 'info', 'warn', 'error'], help="Log level set to info")
    parser.add_argument("--log-file", dest="log", type=str, default=None, help="Log directory (if desired)")
    parser.add_argument("--data-file", dest="data_file", type=str, default=None, help="Data file (if storing)")
    parser.add_argument('--tcp-port', dest='tcp_port', type=int, default=5000, help="Server port number (TCP)")
    parser.add_argument('--udp-port', dest='udp_port', type=int, default=5000, help="Server port number (UDP)")
    return parser.parse_args()

async def main_async(args):
    # create the engine
    with IpcEngine(args) as engine:
        # start the engine
        await engine.start()

        try:
            await engine.receive()
        except KeyboardInterrupt:
            logger.info('Exiting the application')

        await engine.stop()

def main():
    args = parseCmdLineArgs()
    ipc_logging.configure(args)
    asyncio.run(main_async(args))

if __name__ == "__main__":
    main()
