import asyncio
import logging
import json

from generators.curvilinear import CurvilinearGenerator
from generators.linear import LinearGenerator

logger = logging.getLogger(__name__)

class ProfileException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class Profile:
    def __init__(self, args):
        self.args = args
        self.queue = asyncio.Queue()
        self.event = asyncio.Event()
        self.generators = []

    def create_generator(self, profile):
        profile_type = profile['type']
        if profile_type == 'linear':
            generator = LinearGenerator(profile)
        elif profile_type == 'curvilinear':
            generator = CurvilinearGenerator(profile)
        else:
            raise ProfileException(f'invalid profile: type {profile_type} is not recognized')

        self.generators.append(generator)

    async def dispatch(self, client):
        # start all of the generators

        tasks = [asyncio.create_task(g.run(client.send_trade)) for g in self.generators]
        logger.info('dispatch(): waiting for coroutines to finish')
        await asyncio.wait(tasks)
        print(f'dispatch(): checking {client.count}')
        logger.info('dispatch(): finished')

def read_profile(args):
    profile = Profile(args)

    with open(args.profile) as fh:
        configuration = json.load(fh)
        if not isinstance(configuration, list):
            raise ProfileException(f'invalid profile: expecting list, but received {type(configuration)}')

        for entry in configuration:
            profile.create_generator(entry)
    
    return profile
