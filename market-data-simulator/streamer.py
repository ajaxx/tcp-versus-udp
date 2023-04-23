from abc import abstractmethod
import asyncio
import logging

logger = logging.getLogger(__name__)

async def stream_to(message_stream, message_handler, delay, delay_mod):
    logger.debug('stream_to(): startup')

    ii = 0
    for message in message_stream:
        ii += 1
        await message_handler(message)
        # if there is a delay during sending, it will be injected here
        if delay is not None:
            if ((ii % delay_mod) == 0):
                logger.debug(f'stream_to(): delay = {delay}')
                await asyncio.sleep(delay)
    
    logger.debug('stream_to(): shutdown')