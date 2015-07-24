import Queue
import logging
logger = logging.getLogger(__name__)

class QueuePool():
    '''
    Manger Queue pool. 
    '''
    def __init__(self):
        '''
        Create a queue pool
        '''
        self.queue_poll_work = {}
        
    def get_queue(self,key):
        '''
        get the queue of key.
        Args:
            key:the key word for the queue.
        Return:
            return the queue of the key, if not exist, create it.
        Raise:
        '''
        if key not in self.queue_poll_work:
            logger.info('create a new queue,key:%s' %key)
            self.queue_poll_work[key] = Queue.Queue()
        return self.queue_poll_work[key]
