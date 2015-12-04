# pip install websocket-client
from pwn import *
import threading
import Queue
from ictf import iCTF
import requests

_service = "service_name"
_author = "ocean"
_submitter_url = 'http://submitter.ctf.necst.it/submit'

threads = []

q = Queue.Queue()


class Attacker(self):
    flg_re = r"FLG\w{13}"

    def exploit(target):
        """ your main attack routing goes here """

        # here attack the service and get the flags
        """ TARGET FORMAT from iCtf API:
            {
                'team_name' : "Team name",
                'ip_address' : "10.7.<team_id>.2",
                'port' : <int port number>,
                'flag_id' : "Flag ID to steal"
            }"""
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

    def attack():
        t = iCTF.Team("FDwc2R9UN7jA6j2H", "towerofhanoictf@gmail.com")

        while(1):

            targets = t.get_targets(_service)

            # ugly, spawn one thread for each target!
            for t in targets:
                # attack phase
                print "attacking", t
                th = threading.Thread(None, exploit, args=(t,))
                threads.append(th)
                th.start()

            # maybe we should wait for threads to close

            t_info = t.get_tick_info()

            # sleep until the next round
            sleep(t_info['approximate_seconds_left'])


if __name__ == "__main__":
    a = Attacker()
    a.attack()
