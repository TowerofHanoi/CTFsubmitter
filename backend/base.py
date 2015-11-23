class BaseBackend(object):

    client = None
    db = None

    def _connect(self):
        raise NotImplementedError()

    def _close(self):
        raise NotImplementedError()

    def close(self):
        """ cleanup """
        self._close()

    def __init__(self):
        self._connect()

    def insertFlags(self, flags=[]):
        """ insert flag(s) into the DB """
        raise NotImplementedError()

    def getFlags(self, pending=False):
        """ get flags from the backend
        if pending also the flags with 'pending'
        status should be returned """
        raise NotImplementedError()

    #  with statement handlers
    def __enter__(self):
        return self

    def __exit__(self):
        self.close()
