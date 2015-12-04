from tornado import websocket, web, ioloop, gen
from database import logs, stats
from pymongo import ASCENDING
from logger import log
from utils import date_encoder
import json

client_list = []


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    @web.asynchronous
    def nope_open_async(self):
        if self not in client_list:
            client_list.append(self)
        logs.find().limit(
            10).to_list(length=10, callback=self._got_messages)

    def _got_messages(self, messages, error):
        if error:
            raise websocket.WebSocketError(error)
        else:
            for m in messages:
                self.write_message(json.dumps(
                    m, default=date_encoder.default))

    @gen.coroutine
    def open(self):

        if self not in client_list:
            client_list.append(self)
        cursor = logs.find().sort('$natural', ASCENDING).limit(20)
        while(yield cursor.fetch_next):
            r = cursor.next_object()
            r[u'msgtype'] = 'log'
            self.write_message(json.dumps(
                r, default=date_encoder.default))

        cursor = stats.find()
        while (yield cursor.fetch_next):
            r = cursor.next_object()
            r[u'msgtype'] = 'stats'
            self.write_message(json.dumps(
                r, default=date_encoder.default))

    def on_close(self):
        if self in client_list:
            client_list.remove(self)

app = web.Application([
    (r'/websocket', SocketHandler),
])


@gen.coroutine
def push_log():
    cursor = logs.find(tailable=True, await_data=True)

    while True:
        if not cursor.alive:
            # While collection is empty, tailable cursor dies immediately
            yield gen.sleep(1)
            cursor = logs.find(tailable=True, await_data=True)

        if (yield cursor.fetch_next):
            r = cursor.next_object()

            r[u'msgtype'] = 'log'
            msg = json.dumps(
                r, default=date_encoder.default)
            for client in client_list:
                client.write_message(msg)


class StatWarning(Exception):
    pass


def check_stat(r):
    # raise StatWarning("overfloooow")
    pass


@gen.coroutine
def push_stats():
    # unlike the log function we will have to poll
    # the db for updates, aggregating results
    while True:
        yield gen.sleep(15)
        cursor = stats.find()
        while (yield cursor.fetch_next):
            r = cursor.next_object()

            # here check the stats and report any error
            try:
                check_stat(r)
            except Exception as e:
                log.warning(e.message)

            r[u'msgtype'] = 'stats'
            msg = json.dumps(
                r, default=date_encoder.default)

            for client in client_list:
                    client.write_message(msg)


if __name__ == '__main__':
    app.listen(8888)
    push_log()
    push_stats()
    loop = ioloop.IOLoop.current()
    loop.start()
