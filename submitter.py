from __future__ import print_function
from importlib import import_module
from config import config
from logger import log
from config import STATUS
from time import sleep


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
        self.token = config.get("token")
        self.email = config.get("email")
        self.ictf = import_module('ictf')

        super(Submitter, self).__init__()

    def submit(self, flags):
        while(1):
            try:
                ictf = self.ictf.iCTF()
                self.t = ictf.login(self.email, self.token)
                sleep(10)
                break
            except:
                pass

        status = []
        try:
            out = self.t.submit_flag(flags)
        except Exception as e:
            log.error(e.message)
            return [STATUS['unsubmitted']]*len(flags)

        for stat in out:
            if stat == "correct":
                status.append(STATUS['accepted'])
            elif stat == "alreadysubmitted":
                status.append(STATUS['rejected'])
                log.warning("the flag has already been submitted!")
            elif stat == "incorrect":
                status.append(STATUS['rejected'])
                log.error("wrong flags submitted!")
            elif stat == "notactive":
                status.append(STATUS['old'])
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
