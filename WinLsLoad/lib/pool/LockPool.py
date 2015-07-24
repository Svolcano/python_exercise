import threading

class LockPool():
    '''
    lock pool.
    '''
    def __init__(self):
        self.lock_pool = {}

    def get_lock(self, key):
        '''
        get the lock of key.
        Args:
            key:the key word for the lock.
        Return:
            return the lock of key, if not exist, create it.
        Raise:
        '''
        if key not in self.lock_pool:
            self.lock_pool[key] = threading.Lock()

        return self.lock_pool[key]

    def set_lock(self, key, lock):
        self.lock_pool[key] = lock

if __name__ == '__main__':
    from TimeoutLock import TimeoutLock
    lockpool = LockPool()
    print lockpool.get_lock('jmzhang')
    print lockpool.get_lock('qqli')
    print lockpool.get_lock('jsu')
    print lockpool.get_lock('xli')
    print lockpool.get_lock('dliu')
    print lockpool.get_lock('hswang')

    print lockpool.set_lock("sbox",TimeoutLock())
    print lockpool.lock_pool
