from importlib import import_module
from config import config


class SubmitException(Exception):
    """Exception generated when something VERY wrong
    happened during submission, transmission of the flags
    should be retried!"""
    pass


class SubmitterBase(object):

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
        results = self.t.submit_flag(flags)
        accepted = []
        wrong = []

        for r in zip(flags, results):
            if r[1]:
                accepted.append(r[0])
            else:
                wrong.append(r[0])

        return {
            "accepted": accepted,
            "wrong": wrong,
            "expired": []  # the ictf interface won't tell us the difference
        }


class ruCTFeSubmitter(SubmitterBase):

    def __init__(self):
        pwn = import_module('pwn')
        self.remote = pwn.remote
        super(Submitter, self).__init__()

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard"""

        accepted = []
        wrong = []
        old = []
        unsubmitted = list(flags)
        try:
            with self.remote("flags.e.ructf.org", 31337) as r:
                r.read()

                for flag in flags:
                    r.send(flag + "\n")

                    output = r.recv()
                    if "Accepted" in output:
                        accepted.append(flag)
                    elif "Old" in output:
                        old.append(flag)
                    else:
                        wrong.append(flag)

                    unsubmitted.remove(flag)

        except Exception:
            raise SubmitException(
                "an exception was met while submitting flags uh oh...")

        return {
            "accepted": accepted,
            "wrong": wrong,
            "old": old,
            "unsubmitted": unsubmitted,
        }


# choose the submit function here :)
Submitter = iCTFSubmitter
