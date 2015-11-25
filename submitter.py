from importlib import import_module
from config import config
from logger import log

STATUS = {
    "rejected": 0,
    "accepted": 1,
    "old": 2,
    "unsubmitted": 3,
    "pending": 4
}


class SubmitterBase(object):

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard
        returns: a dictionary containing the list
        of accepted/old/wrong flags"""
        raise NotImplementedError()


class DummySubmitter(SubmitterBase):

    def __init__(self):
        self.lose_flags = 1
        self.sleep = import_module('time').sleep
        self.t = 0.2

    def submit(self, flags):
        self.sleep(self.t)
        print "WIIIIIUUUUUUUU"
        print(flags)

        for flag in flags:
            flag["status"] = STATUS["accepted"]

        return flags


class iCTFSubmitter(SubmitterBase):

    def __init__(self):
        token = config.get("token")
        email = config.get("email")
        ictf = import_module('ictf')

        self.t = ictf.Team(token, email)
        super(Submitter, self).__init__()

    def submit(self, flags):

        try:
            results = iter(self.t.submit_flag(flags))
        except Exception:
            log.exception()
            return []

        for flag in flags:
            # updated the status
            status = next(results, STATUS["unsubmitted"])
            flag["status"] = status

        return flags


class ruCTFeSubmitter(SubmitterBase):

    def __init__(self):
        pwn = import_module('pwn')
        self.remote = pwn.remote
        super(Submitter, self).__init__()

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard"""

        try:
            with self.remote("flags.e.ructf.org", 31337) as r:
                r.read()

                for flag in flags:
                    r.send(flag + "\n")

                    output = r.recv()
                    if "Accepted" in output:
                        flag["status"] = STATUS["accepted"]
                    elif "Old" in output:
                        flag["status"] = STATUS["old"]
                    else:
                        flag["status"] = STATUS["rejected"]

        except Exception:
            log.exception(
                "an exception was met while submitting flags uh oh...")

        return flags


# choose the submit function here :)
Submitter = DummySubmitter
