"""Coroutine building block functions

Based on David Beazley's coroutine code from http://dabeaz.com/coroutines/

==========
decorators
==========
- `coroutine(func)`, Calls .next() on func to init func as a coroutine

==================
control coroutines
==================
- `broadcast`, forwards what is sent to it to provided coroutines
- `threaded`, Parallelizes the pipeline with N threads
- `multiprocessed`, Parallelizes the pipeline with N processes

=====
sinks
=====
- `sinks.printer`, Prints whatever is sent to it
- `sinks.locking_printer`, Printer for threaded or multiprocessed

=======
utility
=======
- `utility.cat`, Sends lines from file to target
- `utility.grep`, Sends matching text lines to target
- `utility.dirwalk`, Sends filepaths to target
- `utility.co_filter`, Filters data using a function

"""

__docformat__ = 'restructuredtext'

__all__ = ['coroutine', 'broadcast', 'threaded', 'multiprocessed', 'sinks', 'utility']

import functools
def coroutine(func):
    """
    Initializes func as a coroutine.

    Parameters:

    - `func`: a function to be decorated as a coroutine

    """
    @functools.wraps(func)
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start

@coroutine
def broadcast(*targets):
    """
    Coroutine.  Forwards what is sent to it to each target in targets.

    .send() accepts data to forward
     
    Parameters:

    - `targets`: a list of coroutines, next stage of pipeline

    """
    while True:
        try:
            item = (yield)
            for target in targets:
                target.send(item)
        except GeneratorExit:
            for target in targets:
                target.close()
            return

import threading
import Queue
class threaded(object):
    """
    Class acting as a coroutine.  Creates specified number of threads
    and passes data to them via a queue.  Threads take data as soon as they
    are free and it is available then pass it to their targets.

    """
    def __init__(self, num_threads, wrapped_target):
        """
        Spawn threads to send data to target.

        Parameters:

        - `num_threads`: an integer, number of threads to spawn
        - `wrapped_target`: coroutine wrapped in function, next stage of
                            pipeline
        
        example::
         
            # using the coroutines grep and printer, create a wrapped coroutine
            wrapped_co = lambda : grep(r'important', printer())
            # create the rest of the pipeline
            # it will cat some file into 4 threads that will grep and print
            pipeline = cat(threaded(4, wrapped_co))
             
            pipeline.send('textfile.txt')

        """
        self._stopEvent = threading.Event()
        self._wrapped_target = wrapped_target
        self._num_threads = num_threads
        self.threaded = self._threaded()

    @coroutine
    def _threaded(self):
        messages = Queue.Queue()
        def run_target(stopEvent):
            target = self._wrapped_target()
            while not stopEvent.is_set():
                item = messages.get()
                if item is GeneratorExit:
                    break
                else:
                    target.send(item)
            target.close()
        
        for i in xrange(self._num_threads):
            threading.Thread(target=run_target, args=(self._stopEvent, )).start()
        try:
            while True:
                item = (yield)
                messages.put(item)
        except GeneratorExit:
            for i in xrange(self._num_threads):
                messages.put(GeneratorExit)
    
    def stop(self):
        """Signal the threads to stop."""
        self._stopEvent.set()

    def send(self, arg):
        """
        Simulates coroutine .send() method.  Accepts data to forward to
        target coroutines.

        Parameters:

        - `arg`: an object, data to be forwarded

        """
        self.threaded.send(arg)

    def close(self):
        """
        Simulates coroutine .close() method.  Closes this coroutine and
        signals target coroutine to close().

        """
        self.threaded.close()

import multiprocessing
class multiprocessed(object):
    """
    Class acting as a coroutine that passes data on to its target via a
    queue and a multiprocessing.Process().

    """
    def __init__(self, num_processes, target):
        """
        Spawn processes to send data to target.

        Parameters:

        - `num_processes`: an integer, number of processes to spawn
        - `target`: a coroutine, next stage of pipeline

        """
        self._stopEvent = multiprocessing.Event()
        self._target = target
        self._num_processes = num_processes
        self.multiprocessed = self._multiprocessed()

    @coroutine
    def _multiprocessed(self):
        target = self._target
        messages = multiprocessing.Queue()
        def run_target(stopEvent):
            while not stopEvent.is_set():
                item = messages.get()
                if item is GeneratorExit:
                    break
                else:
                    target.send(item)
            target.close()
            
        for i in xrange(self._num_processes):
            multiprocessing.Process(
                target=run_target, args=(self._stopEvent, )).start()
        try:
            while True:
                item = (yield)
                messages.put(item)
        except GeneratorExit:
            for i in xrange(self._num_processes):
                messages.put(GeneratorExit)
    
    def stop(self):
        """Signal the processes to stop."""
        self._stopEvent.set()

    def send(self, arg):
        """
        Simulates coroutine .send() method.  Accepts data to forward to
        target coroutines.

        Parameters:

        - `arg`: an object, data to be forwarded

        """
        self.multiprocessed.send(arg)

    def close(self):
        """
        Simulates coroutine .close() method.  Closes this coroutine and
        signals target coroutine to close().

        """
        self.multiprocessed.close()

import sinks
import utility
