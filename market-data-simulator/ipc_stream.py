#!/usr/bin/python3

import asyncio
import logging
import logging.handlers
import argparse

import ipc_logging
import ipc_profile

from tcp_client import TCP_Client
from udp_client import UDP_Client

logger = logging.getLogger(__name__)

# Parses command line arguments
def parseCmdLineArgs():
    parser = argparse.ArgumentParser(description="Reliable TCP Client")
    parser.add_argument("--debug", dest="log_level", action="store_const", const='debug', help="Log level set to debug")
    parser.add_argument("--log-level", dest="log_level", action="store", choices=['debug', 'info', 'warn', 'error'], help="Log level set to info")
    parser.add_argument("--log-file", dest="log", type=str, default=None, help="Log directory (if desired)")
    parser.add_argument("--profile", dest="profile", type=str, required=True, default=None, help="Performance profile")
    parser.add_argument('--proto', choices=['tcp', 'udp'], required=True, help="Protocol for stream")
    parser.add_argument("host", type=str)
    parser.add_argument("port", type=int)
    return parser.parse_args()

async def create_tcp_client(args):
    # we create a client, which establishes a connection
    client = TCP_Client()
    # connect to the endpoint
    await client.connect(args.host, args.port)
    # return the client
    return client

async def create_udp_client(args):
    # we create a client, which establishes a connection
    client = UDP_Client()
    # connect to the endpoint
    await client.connect(args.host, args.port)
    # return the client
    return client

async def create_client(args):
    if args.proto == 'tcp':
        return await create_tcp_client(args)
    elif args.proto == 'udp':
        return await create_udp_client(args)

async def main_async(args):
    profile = ipc_profile.read_profile(args)
    # create the client
    client = await create_client(args)
    # send messages to the client
    await profile.dispatch(client)
    # we terminate the connection
    await client.close()
    print(f'{client.count} messages transmitted')

def main():
    args = parseCmdLineArgs()
    ipc_logging.configure(args)
    asyncio.run(main_async(args))

if __name__ == "__main__":
    main()
