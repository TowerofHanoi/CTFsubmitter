# pip install websocket-client
from pwn import *
import threading
import Queue
from ictf import Team

_service = "service_name"
_author = "ocean"
_submitter_url = 'http://submitter.ctf.necst.it/submit'

global flags
flags = []
threads = []

global submitted_flags
submitted_flags = []

q = Queue.Queue()

flg_re = r"FLG\w{13}"


def attack(target):
    """ your main attack routing goes here """

    # here attack the service and get the flags
    print target

    flags = [
        "FLG1234567890123",
        "FLGABCDEFGHI0123"]

    submit_flags(flags, target)
    return


def submit_flags(flags, target):
    requests.post(
        _submitter_url,
        data={
            "service": _service,
            "team": target['team_name'],
            "flags": flags,
            "name": _author})


if __name__ == "__main__":

    current_tick = 0
    t = Team("FDwc2R9UN7jA6j2H", "towerofhanoictf@gmail.com")

    while(1):

        t_info = t.get_tick_info()

        # sleep until the next round
        sleep(t_info['approximate_seconds_left'])

        targets = t.get_targets(_service)

        # ugly, spawn one thread for each target!
        for t in targets:
            # attack phase
            print "attacking", t
            th = threading.Thread(None, attack, args=(t,))
            threads.append(th)
            th.start()
