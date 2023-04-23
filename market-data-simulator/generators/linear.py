import asyncio
import logging
import trade

logger = logging.getLogger(__name__)

class LinearGenerator:
    def __init__(self, config):
        self.delay = config['delay']
        self.delay_modulus = config['delay_modulus']
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
        print(f'producing {self.num_messages} for {self.symbol}')
        for ii in range(0, self.num_messages):
            handler(trade.rand(self.symbol, ii))
            # if there is a delay during sending, it will be injected here
            if self.delay is not None:
                if ((ii % self.delay_modulus) == 0):
                    logger.info(f'run({self.symbol}:{ii}): sleeping {self.delay} after {self.delay_modulus} iterations')
                    await asyncio.sleep(self.delay)
        
        logger.debug('run(): shutdown')
