from __future__ import absolute_import, print_function, unicode_literals
from threading import Thread, Event, Lock
from time import sleep
from config import config
import sys

from backend.mongodb import MongoBackend

from logger import log

from submitter import Submitter

s = Submitter()


def safe_say(msg):
    print('\n{0}'.format(msg), file=sys.__stderr__)


class WorkerPool(object):
    """ this class will manage a basic pool of threads that will
    submit the flags to the scoreboard.
    since most of the time we are involved in I/O we can just use
    some threads since GIL will be released.
    Please read this before freaking out:
    http://jessenoller.com/2009/02/01/python-threads-and-the-global-interpreter-lock/
    """

    def __init__(self, backend=None):
        self.backend = backend
        self.cancel_event = Event()

        # the pool will contain our consumer threads
        self.pool = []

        for i in xrange(0, config.get("workers", 4)):
            # create a number of worker threads that will
            # "consume" the flags, submitting them
            t = Worker(
                backend,
                self.cancel_event,
                config.get("worker_sleep_time", 18),
                self.lock)

            self.pool.append(t)
            t.start()

    def close(self):
        """ eventually free up connections and so on """

        self.cancel_event.set()

        for t in self.pool:
            t.join()  # wait for complete
            self.pool.remove(t)


class Worker(Thread):
    """Worker thread that will submit the flag to the service"""
    def __init__(self, backend, cancelled, sleep_time, lock):
        Thread.__init__(self)
        self.sleep_time = sleep_time
        self.backend = backend
        self.cancelled = cancelled
        self.lock = lock

    def run(self):
        while not self.cancelled.is_set():
            # yes sorry we go to use a lock :(
            # mongo doesn't allow find_and_modify
            # on multiple documents
            task = self.backend.get_task()

            if not task:
                # no flags available! backoff!
                sleep(self.sleep_time)
            else:

                status = s.submit(task['flags'])
                # update the flags that changed status!
                try:
                    self.backend.update_flags(task, status)
                except ValueError as e:
                    log.exception(e)


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
