from tornado import websocket, web, ioloop, gen
from datetime import datetime
from database import logs


loop = ioloop.IOLoop()

client_list = []


class SocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in client_list:
            client_list.append(self)

    def on_close(self):
        if self in client_list:
            client_list.remove(self)

app = web.Application([
    (r'/websocket', SocketHandler),
])


@gen.coroutine
def get_log():
    cursor = logs.find(tailable=True, await_data=True)
    while True:
        if not cursor.alive:
            # While collection is empty, tailable cursor dies immediately
            yield gen.Task(loop.add_timeout, datetime.timedelta(seconds=1))
            cursor = logs.find(tailable=True, await_data=True)

        if (yield cursor.fetch_next):
            r = cursor.next_object()
            for client in client_list:
                client.write_message(r)

if __name__ == '__main__':
    app.listen(8888)
    loop.start()
