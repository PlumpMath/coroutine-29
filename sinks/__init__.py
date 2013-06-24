__all__ = ['printer', 'locking_printer']

from coroutine import coroutine

@coroutine
def printer():
    """
    Coroutine.  Prints what is sent to it.
    
    .send() accepts data to print

    """
    while True:
        try:
            line = (yield)
        except GeneratorExit:
            return

        print line

@coroutine
def locking_printer(lock):
    """
    Coroutine.  Prints what is .sent() to it.  Locks on 'lock'.

    .send() accepts data to print

    Parameters:

    - `lock`: threading.Lock or multiprocessing.Lock (a semaphore will
              work as well)

    """
    while True:
        try:
            line = (yield)
        except GeneratorExit:
            return

        lock.acquire()
        print line
        lock.release()
