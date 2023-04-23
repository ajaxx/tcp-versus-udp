import asyncio
import logging
import math
import trade

logger = logging.getLogger(__name__)

class CurvilinearGenerator:
    def __init__(self, config):
        self.delay = config['delay']
        self.delay_modulus = config['delay_modulus']
        self.increment = config.get('increment', 1.0)
        self.symbol = config['symbol']
        self.num_messages = config['num_messages']
    
    def __dict__(self):
        return {
            'symbol': self.symbol,
            'num_messages': self.num_messages,
            'delay': self.delay,
            'delay_modulus': self.delay_modulus
        }
    
    def __repr__(self):
        return repr(self.__dict__())
    
    async def run(self, handler):
        logger.info('run(): starting')

        try:
            angle = 0
            angle_increment = math.radians(self.increment)
            for ii in range(0, self.num_messages):
                handler(trade.rand(self.symbol, ii))
                if ((ii % self.delay_modulus) == 0):
                    # curve
                    angle += angle_increment
                    # create the delay multiplier as a function of the sine function
                    curve = math.sin(angle) + 1.0
                    delay = self.delay * curve

                    logger.info(f'run({self.symbol}:{ii}): sleeping {delay} after {self.delay_modulus} iterations')
                    await asyncio.sleep(self.delay)
        finally:
            logger.debug('run(): shutdown')
