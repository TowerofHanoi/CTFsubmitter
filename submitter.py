from importlib import import_module
from config import config
from logger import log
from itertools import repeat


class SubmitterBase(object):

    status = {
        "rejected": 0,
        "accepted": 1,
        "old": 2,
        "unsubmitted": 3
    }

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard
        returns: a dictionary containing the list
        of accepted/old/wrong flags"""
        raise NotImplementedError()


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
            return zip(flags, repeat(self.status["unsubmitted"], len(flags)))

        return zip(flags, [int(r) for r in results])


class ruCTFeSubmitter(SubmitterBase):

    def __init__(self):
        pwn = import_module('pwn')
        self.remote = pwn.remote
        super(Submitter, self).__init__()

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard"""

        results = []
        unsubmitted = []

        try:
            with self.remote("flags.e.ructf.org", 31337) as r:
                r.read()

                while flags:
                    flag = flags.pop()
                    r.send(flag + "\n")

                    output = r.recv()
                    if "Accepted" in output:
                        results.append(self.status["accepted"])
                    elif "Old" in output:
                        results.append(self.status["old"])
                    else:
                        results.append(self.status["rejected"])

        except Exception:
            log.exception(
                "an exception was met while submitting flags uh oh...")

            unsubmitted = (
                [self.status["unsubmitted"]]*(len(flags)-len(results))
            )

        return zip(flags, results+unsubmitted)


# choose the submit function here :)
Submitter = iCTFSubmitter
