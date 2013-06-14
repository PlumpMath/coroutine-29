from coroutine import coroutine

@coroutine
def cat(target):
    """Coroutine.  Opens file and sends its contents, line by line, to target.

    .send() accepts the path of a file to read

    arguments:
    target - coroutine to send lines to
    """
    while True:
        try:
            filepath = (yield)
            
            with open(filepath, 'r') as f:
                for line in f:
                    target.send(line)

        except GeneratorExit:
            target.close()
            return

import re
@coroutine
def grep(pattern, target):
    """Coroutine.  Forwards a line of text to its target if pattern is matched.

    .send() accepts a string

    arguments:
    pattern - regex pattern to match
    target - coroutine to forward matching results to.
    """
    regex = re.compile(pattern)
    while True:
        try:
            line = (yield)
            match = regex.search(line)
            if match is not None:
                target.send(line)
        except GeneratorExit:
            target.close()
            return

import os
@coroutine
def dirwalk(target):
    """Coroutine.  Walk a directory structure and send file paths to target.
    
    .send() accepts the name of a directory to walk.

    arguments:
    target - coroutine to send file paths to
    """
    while True:
        try:
            dirpath = (yield)
            for root, dirs, files in os.walk(dirpath):
                for filename in files:
                    filepath = os.path.sep.join([root, filename])
                    target.send(filepath)
        except GeneratorExit:
            target.close()
            return

@coroutine
def co_filter(func, target):
    """Coroutine.  Applies function 'func' to data sent to it.  If func returns
    true the data is forwarded.

    .send() accepts data to be filtered

    arguments:
    func   - filter function used to screen data
    target - coroutine to forward data to
    """
    while True:
        try:
            number = (yield)
            if func(number):
                target.send(number)
        except GeneratorExit:
            target.close()
            return
