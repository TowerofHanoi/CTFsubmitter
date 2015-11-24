from importlib import import_module
from config import config
from logger import log
from itertools import izip_longest, repeat

STATUS = {
    "rejected": 0,
    "accepted": 1,
    "old": 2,
    "unsubmitted": 3
}


class SubmitterBase(object):

    @staticmethod
    def results(flags, results):
        """ return an iterator returning tuples contaning the flag
        and the status of the flag, later you can use this
        structure in the backend to search/insert/update
        flags accordingly :)"""

        return izip_longest(
            flags, results,
            fillvalue=STATUS['unsubmitted'])

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard
        returns: a dictionary containing the list
        of accepted/old/wrong flags"""
        raise NotImplementedError()


class DummySubmitter(SubmitterBase):

    def __init__(self):
        self.lose_flags = 2
        self.sleep = import_module('time').sleep
        self.t = 0.2

    def submit(self, flags):
        self.sleep(self.t)
        print flags
        return self.results(
            flags,
            repeat(STATUS['unsubmitted']),
            (len(flags)-self.lose_flags)
        )


class iCTFSubmitter(SubmitterBase):

    def __init__(self):
        token = config.get("token")
        email = config.get("email")
        ictf = import_module('ictf')

        self.t = ictf.Team(token, email)
        super(Submitter, self).__init__()

    def submit(self, flags):

        try:
            results = self.t.submit_flag(flags)
        except Exception:
            log.exception()
            results = []

        return self.results(flags, [int(r) for r in results])


class ruCTFeSubmitter(SubmitterBase):

    def __init__(self):
        pwn = import_module('pwn')
        self.remote = pwn.remote
        super(Submitter, self).__init__()

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard"""

        results = []

        try:
            with self.remote("flags.e.ructf.org", 31337) as r:
                r.read()

                while flags:
                    flag = flags.pop()
                    r.send(flag + "\n")

                    output = r.recv()
                    if "Accepted" in output:
                        results.append(STATUS["accepted"])
                    elif "Old" in output:
                        results.append(STATUS["old"])
                    else:
                        results.append(STATUS["rejected"])

        except Exception:
            log.exception(
                "an exception was met while submitting flags uh oh...")

        return self.results(flags, results)


# choose the submit function here :)
Submitter = DummySubmitter
