# pip install websocket-client
from pwn import *
import threading
import Queue
from ictf import iCTF
import requests

_service = "service_name"
_author = "ocean"
_submitter_url = 'http://submitter.ctf.necst.it/submit'

q = Queue.Queue()

ic = iCTF()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Attacker():
    flg_re = r"FLG\w{13}"

    @staticmethod
    def _exploit(target):
        """

        target = {
                'team_name' : "Team name",
                'ip_address' : "10.7.<team_id>.2",
                'port' : <int port number>,
                'flag_id' : "Flag ID to steal"}
        """
        flags = [
            "FLG1234567890123",
            "FLGABCDEFGHI0123"]

        return flags

    def exploit(self, target):
        flags = self._exploit(target)
        return self.submit_flags(flags, target)

    def submit_flags(self, flags, target):
        r = requests.post(
            _submitter_url,
            data={
                "service": _service,
                "team": target['team_name'],
                "flags": flags,
                "name": _author})
        return r.text

    def attack(self):

        while(1):
            threads = []
            team = ic.login("towerofhanoictf@gmail.com", "FDwc2R9UN7jA6j2H")
            targets = team.get_targets(_service)

            # ugly, spawn one thread for each target!
            for t in targets['targets']:
                # attack phase
                print "attacking", t
                th = threading.Thread(None, self.exploit, args=(t,))
                threads.append(th)
                th.start()

            # maybe we should wait for threads to close

            while threading.active_count() > 1:
                time.sleep(0.5)

            t_info = team.get_tick_info()

            # sleep until the next round
            sleep(t_info['approximate_seconds_left'])
            while(team.get_tick_info()['tick_id'] <= t_info['tick_id']):
                sleep(1)


if __name__ == "__main__":
    a = Attacker()
    a.attack()
