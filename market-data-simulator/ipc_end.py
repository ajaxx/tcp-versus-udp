#!/usr/bin/python3

import asyncio
import logging
import logging.handlers
import argparse
import packet

import ipc_logging
from tcp_client import TCP_Client

logger = logging.getLogger(__name__)

# Parses command line arguments
def parseCmdLineArgs():
    parser = argparse.ArgumentParser(description="Control application")
    parser.add_argument("--debug", dest="log_level", action="store_const", const='debug', help="Log level set to debug")
    parser.add_argument("--log-level", dest="log_level", action="store", choices=['debug', 'info', 'warn', 'error'], help="Log level set to info")
    parser.add_argument("--log-file", dest="log", type=str, default=None, help="Log directory (if desired)")
    parser.add_argument("host", type=str)
    parser.add_argument("port", type=int)
    return parser.parse_args()


async def main_async(args):
    # we create a client, which establishes a connection
    client = TCP_Client()
    # connect to the endpoint
    await client.connect(args.host, args.port)
    # send end
    client.send_message(packet.end())
    # we terminate the connection
    await client.close()

def main():
    args = parseCmdLineArgs()
    ipc_logging.configure(args)
    asyncio.run(main_async(args))

if __name__ == "__main__":
    main()
