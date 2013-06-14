"""Coroutine building block functions

Based on David Beazley's coroutine code from http://dabeaz.com/coroutines/

--decorators--
coroutine(func) - Calls .next() on func to init func as a coroutine

--control coroutines--
broadcast      - forwards what is sent to it to each coroutine provided as an
                 argument
threaded       - Creates N threads and uses them to parallelize the pipeline
multiprocessed - Creates N processes and uses them to parallelize the pipeline

--sinks--
sinks.printer         - Prints whatever is sent to it.
sinks.locking_printer - Locks around a Lock object and prints whatever is sent to
                        it.

--utility--
utility.cat       - Opens file and sends contents, line by line, to target
utility.grep      - Forwards a line of text to its target if pattern is matched
utility.dirwalk   - Walk a directory structure and send file paths to target
utility.co_filter - Filters data using a function
"""

from coroutine import coroutine, broadcast, threaded, multiprocessed
import sinks
import utility
