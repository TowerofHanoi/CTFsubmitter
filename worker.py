from __future__ import absolute_import, print_function, unicode_literals
from threading import Thread, Event
from time import sleep
import logging
from config import config
import sys

from backend.mongodb import MongoBackend

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    level=logging.DEBUG)

log = logging.getLogger(__name__)


def safe_say(msg):
    print('\n{0}'.format(msg), file=sys.__stderr__)


class WorkerPool(object):
    """ this class will be a basic submitter
    since most of the time we are involved in I/O
    we can just use some threads since GIL will be released
    please read this before freaking out:
    http://jessenoller.com/2009/02/01/python-threads-and-the-global-interpreter-lock/
    """

    def __init__(self, backend=None):
        self.backend = backend

        # the pool will contain our consumer threads
        self.pool = []

        for i in xrange(0, config.get("workers", 4)):
            # create a number of worker threads that will
            # "consume" the flags, submitting them
            t = Worker(backend)
            self.pool.append(t)
            t.start()

    def close(self):
        """ eventually free up connections and so on """

        for t in self.pool:
            t.cancel()  # signal all threads to complete

        for t in self.pool:
            t.join()  # wait for complete
            self.pool.remove(t)


class Worker(Thread):
    """Worker thread that will submit the flag to the service"""
    def __init__(self, backend):
        Thread.__init__(self)
        self.backend = backend
        self.cancelled = False

    def run(self):
        while not self.cancelled:
            flags = self.backend.getFlags()

            if not flags:
                # no flags available! backoff!
                s = config.get("worker_sleep_time", 1)
                log.debug("no flags, backing off for %d seconds", s)
                sleep(s)
                continue

    def cancel(self):
        self.cancelled = True


if __name__ == "__main__":
    backend = MongoBackend()

    # keep the main thread alive
    try:
        print("Running! Hit CTRL+C to exit!")
        pool = WorkerPool(backend)
        while(1):
            sleep(10)
    except (KeyboardInterrupt, SystemExit):
            pool.close()
    finally:
        safe_say("Thanks for flying with us! :)")
