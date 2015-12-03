import logging
import getpass
from datetime import datetime
from socket import gethostname
from backend.mongodb import MongoBackend

backend = MongoBackend()


class MongoFormatter(logging.Formatter):
    def format(self, record):
        """Format exception object as a string"""
        data = record.__dict__.copy()

        if record.args:
            msg = record.msg % record.args
        else:
            msg = record.msg

        data.update(
            username=getpass.getuser(),
            time=datetime.utcnow(),
            host=gethostname(),
            msg=msg,
            args=tuple(unicode(arg) for arg in record.args)
        )
        if 'exc_info' in data and data['exc_info']:
            data['exc_info'] = self.formatException(data['exc_info'])
        return data


class MongodbHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)
        self.formatter = MongoFormatter()

    def emit(self, record):
        msg = self.format(record)
        backend.insert_logmsg(msg)

logging.basicConfig(
    format='[%(asctime)s] %(message)s',
    level=logging.DEBUG)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
if not log.handlers:
    log.addHandler(MongodbHandler())
