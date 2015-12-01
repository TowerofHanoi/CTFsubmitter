from tornado import websocket, web, ioloop, gen
from datetime import datetime
from config import config

import motor
import settings

connection = motor.MotorClient(settings.MONGO_HOST, settings.MONGO_PORT).open_sync()

loop = ioloop.IOLoop()

cl = []


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)

    def on_close(self):
        if self in cl:
            cl.remove(self)

app = web.Application([
    (r'/websocket', SocketHandler),
])


@gen.coroutine
def tail_example():
    results = []
    collection = db.my_capped_collection
    cursor = collection.find(tailable=True, await_data=True)
    while True:
        if not cursor.alive:
            # While collection is empty, tailable cursor dies immediately
            yield gen.Task(loop.add_timeout, datetime.timedelta(seconds=1))
            cursor = collection.find(tailable=True, await_data=True)

        if (yield cursor.fetch_next):
            results.append(cursor.next_object())
            print results

if __name__ == '__main__':
    app.listen(8888)
    loop.start()
