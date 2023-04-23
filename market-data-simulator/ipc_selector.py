import logging
import selectors
import threading

logger = logging.getLogger(__name__)

class IpcSelector:
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.loop_event = threading.Event()
        
    def stop(self):
        logger.info('stop(): stopping selector loop')
        self.loop_event.set()

    async def receive(self):
        logger.debug('receive(): starting')

        try:
            has_events = True
            # handle the next incoming packet
            while not self.loop_event.is_set() or has_events:
                events = self.selector.select(1.0)
                if events:
                    has_events = True
                    for key, mask in events:
                        callback = key.data
                        await callback(key.fileobj)
                else:
                    has_events = False
            
            logger.debug('receive(): shutting down')
            self.selector.close()
        except Exception as e:
            logger.exception(f'exception occurred during processing', exc_info = e)
        finally:
            print('exiting')
    
    def unregister(self, sock):
        self.selector.unregister(sock)

    def register(self, sock, mask, data):
        self.selector.register(sock, mask, data)