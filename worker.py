from threading import Thread
from time import sleep
from Queue import Queue


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
                sleep(config.get("worker_sleep_time", 5))
                continue

    def cancel(self):
        self.cancelled = True
