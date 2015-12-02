from __future__ import absolute_import, print_function, unicode_literals

from bottle import post, get, run, request, abort, template, static_file, route
from config import config
import re
import os

from ipaddress import ip_address

from backend.mongodb import MongoBackend
from logger import log

# define a regex for flags
flag_regex = config.get("flag_regex", "^\w{31}=$")
service_regex = "^\w{0,32}$"

backend = MongoBackend()


@route('/static/<path:path>')
def callback(path):
    return static_file(path, './static')


@get('/stats')
def stats():
    return template('templates/stats.html')


#  web interface here
@post('/submit')
def submit_flag():
    name = request.forms.get('name')
    team = request.forms.get('team')
    service = request.forms.get('service')
    flags = request.forms.getall('flags')
    ip = request.environ.get('REMOTE_ADDR').decode('utf-8')
    ip = int(ip_address(ip))

    if not flags or not team or not service:
        # bad request
        abort(400)

    try:
        team = int(team)
    except:
        abort(400, "team should be a number!")

    if not re.match(service_regex, service):
        abort(400, "wrong format for service \w{32}")

    backend.insert_flags(
            team, service, flags,
            name, ip)

if __name__ == "__main__":
    if 'BOTTLE_CHILD' not in os.environ:
        log.info("Submitter service started")

    backend.cold_restart()
    # try to set all the pending task to unsubmitted (retry)
    run(
        host='localhost',
        port=8080,
        reloader=True,
        debug=config.get("debug", False))
