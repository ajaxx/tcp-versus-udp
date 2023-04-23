#!/usr/bin/python

import os
import math
import json
import random
import argparse
import logging
import datetime

# Parses command line arguments
def parseCmdLineArgs ():
    parser = argparse.ArgumentParser (description="Web Client")
    parser.add_argument ('-d', '--debug', dest='debug', action='store_true', help="Enable debugging logs")
    parser.add_argument ('-l', dest='log', type=str, default=None, help="Log directory (if desired)")
    parser.add_argument ('-s', '--seed', type=int, default=None, help="The randomizer seed")
    parser.add_argument ('-o', '--out', type=str, default=None, help="The output file")
    parser.add_argument ('url')
    return parser.parse_args()

def initializeLogger(args):
    logging_level = logging.DEBUG if args.debug else logging.INFO
    logging_handlers = None
    if args.log is not None:
        logging_handlers = [
            logging.handlers.RotatingFileHandler(args.log),
            logging.StreamHandler()
        ]

    logging.basicConfig(level = logging_level, handlers = logging_handlers)

def initializeRandomizer(args):
    if args.seed is not None:
        random.seed(int(args.seed))

def createSymbolTrafficProfile(args, symbol):
    """Creates the profile for the specified symbol"""
    # we do not obtain real market data because it is not important, but we
    # will construct a theoretical rate at which data is produced for this
    # symbol
    velocity = random.randint(1, 100)
    seed = random.randint(0, math.
    return (symbol, velocity, seed)

def main():
    args = parseCmdLineArgs ()

    initializeLogger(args)
    initializeRandomizer(args)

    with open('nyse-listed.json', 'r') as fh:
        listed_nyse = json.load(fh)
    with open('other-listed.json', 'r') as fh:
        listed_other = json.load(fh)

    symbols = list()
    num_symbols = (100, 100)

    for ii in range(0, num_symbols[0]):
        index = random.randint(0, len(listed_nyse))
        # add the symbol to the list
        symbols.append(listed_nyse[index]['ACT Symbol'])
        # remove the symbol from the list
        del listed_nyse[index]
    
    for ii in range(0, num_symbols[1]):
        index = random.randint(0, len(listed_other))
        # add the symbol to the list
        symbols.append(listed_other[index]['ACT Symbol'])
        # remove the symbol from the list
        del listed_other[index]

    with open('symbols.json', 'w') as fh:
        json.dump(symbols, fh, indent = 4)

if __name__ == '__main__':
    main()