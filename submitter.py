from bottle import post, run, request, abort
from config import config
from pymongo import MongoClient
from worker import Worker

import re

from backend.mongodb import MongoBackend


client = MongoClient('andrototal-dev', 27017)
db = client[config.get('flags_db', "flagsdb")]

# define a regex for flags
flag_regex = config.get("flag_regex", "^\w{31}=$")
service_regex = "^\w{32}$"


class Submitter(object):
    """ this class will be a basic submitter
    since most of the time we are involved in I/O
    we can just use some threads since GIL will be released
    please read this before freaking out:
    http://jessenoller.com/2009/02/01/python-threads-and-the-global-interpreter-lock/
    """

    def __init__(self, backend=None):
        self.backend = backend

        # the pool will contain our consumer threads
        self.pool = []

        for i in xrange(0, config.get("workers", 4)):
            # create a number of worker threads that will
            # "consume" the flags, submitting them
            self.pool.append(Worker(backend))

    def close(self):
        """ eventually free up connections and so on """

        for t in self.pool:
            t.cancel()  # signal all threads to complete

        for t in self.pool:
            t.join()  # wait for complete


backend = MongoBackend()
submitter = Submitter(backend)


#  web interface here
@post('/submit')
def submit_flag():
    team = request.forms.get('team')
    service = request.forms.get('service')
    flags = request.forms.getall('flags')

    if not flags or not team or not service:
        # bad request
        abort(400)

    try:
        team = int(team)
    except:
        abort(400, "team should be a number!")

    if not re.match(service_regex, service):
        abort(400, "wrong format for service \w{32}")

    backend.insert_flags(team, service, flags)


if __name__ == "__main__":
    try:
        run(
            host='localhost',
            port=8080,
            reloader=True,
            debug=config.get("debug", False))
    except:
        print "Exception, cleaning up"
        # here we clean up the threads mess (:
    finally:
        submitter.close()
        print "Thank for flying with us! :)"
