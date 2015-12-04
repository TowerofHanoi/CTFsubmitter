from __future__ import print_function
from importlib import import_module
from config import config
from logger import log
from config import STATUS


class SubmitterBase(object):

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard
        returns: a list containing the status for every flag"""
        raise NotImplementedError()


class DummySubmitter(SubmitterBase):

    def __init__(self):
        self.lose_flags = 1
        self.sleep = import_module('time').sleep
        self.t = 0.2

    def submit(self, flags):
        status = []
        self.sleep(self.t)
        ff = []
        for flag in flags:
            status.append(STATUS["accepted"])
            ff.append(flag['flag'])
        print("FLAAAAAAAGS %s" % ff)

        return status


class iCTFSubmitter(SubmitterBase):

    def __init__(self):
        token = config.get("token")
        email = config.get("email")
        ictf = import_module('ictf')
        self.ictf = ictf.iCTF()

        self.t = self.ictf.Team(token, email)
        super(Submitter, self).__init__()

    def submit(self, flags):

        status = []
        try:
            out = self.t.submit_flag(flags)
        except Exception as e:
            log.exception(e)
            return [STATUS['unsubmitted']]*len(flags)

        for stat in out:
            if stat == "correct":
                status.append(STATUS['accepted'])
            elif stat == "alreadysubmitted":
                status.append(STATUS['wrong'])
                log.warning("the flag has already been submitted!")
            elif stat == "incorrect":
                status.append(STATUS['wrong'])
                log.error("wrong flags submitted!")
            elif stat == "notactive":
                status.append(STATUS['wrong'])
                log.error("unactive!")
            else:
                status.append(STATUS['unsubmitted'])
                log.error("too many incorrect STAHP!!!")

        if len(status) < len(flags):
            status += [STATUS['unsubmitted'] for i in range(
                            len(flags)-len(status))]

        return status


class ruCTFeSubmitter(SubmitterBase):

    def __init__(self):
        pwn = import_module('pwn')
        self.remote = pwn.remote
        super(Submitter, self).__init__()

    def submit(self, flags):
        """ this function will submit the flags to the scoreboard"""
        status = []

        try:
            with self.remote("flags.e.ructf.org", 31337) as r:
                r.read()

                for flag in flags:
                    r.send(flag + "\n")

                    output = r.recv()
                    if "Accepted" in output:
                        s = STATUS["accepted"]
                    elif "Old" in output:
                        s = STATUS["old"]
                    else:
                        s = STATUS["rejected"]

                    status.append(s)

        except Exception as e:
            log.exception(e)

        return status


# choose the submit function here :)
Submitter = iCTFSubmitter
