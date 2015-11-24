from pymongo import MongoClient
from base import BaseBackend
from config import config
from submitter import STATUS


class MongoBackend(BaseBackend):

    def _connect(self):
        self.client = MongoClient(
            config['mongodb']['host'],
            config['mongodb']['port'])
        self.db = self.client["submitter"]
        self.flagz = self.db['flagz']

    def _close(self):
        self.client.close()

    def get_flags(self, N=config.get("", 80)):
        # flags = self.flagz.aggregate()
        cursor = self.flagz.find({'status': STATUS['unsubmitted']}).limit(N)
        flags = [f for f in cursor]
        return flags

    def update_flags(self, flags):
        pass

    def insert_flags(self, team, service, flags):
        self.flagz.insert_many(
            [{
                'flag': i,
                'team': team,
                'service': service,
                'status': STATUS['unsubmitted'],
            } for i in flags])
