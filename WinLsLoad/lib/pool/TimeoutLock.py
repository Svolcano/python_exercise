
import time
import threading

class TimeoutLock:

    def __init__(self):
        self.lock = threading.Lock()
    
    def acquire(self, timeout):
        endtime = time.time() + timeout
        delay = 0.0005 # 500 us -> initial delay of 1 ms
        while True:
            gotit = self.lock.acquire(0)
            if gotit:
                break
            remaining = endtime - time.time()
            if remaining <= 0:
                break
            delay = min(delay * 2, remaining, .05)
            time.sleep(delay)

        return gotit

    def release(self):
        self.lock.release()


if __name__ == '__main__':
    lock = TimeoutLock()
    print lock.acquire(60)
    lock.release()

