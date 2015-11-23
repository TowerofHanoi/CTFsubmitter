from threading import Thread
from time import sleep
from Queue import Queue
import logging
from config import config

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    level=logging.DEBUG)

log = logging.getLogger(__name__)


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
                s = config.get("worker_sleep_time", 5)
                log.debug("no flags, backing off for %d seconds", s)
                sleep(s)
                continue

    def cancel(self):
        self.cancelled = True
