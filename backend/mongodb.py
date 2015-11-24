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

        if cursor:
            flags = []
            ids = []
            for flag in cursor:
                flags.append(flag)
                ids.append(flag["_id"])
            self.flagz.update(
                {"_id": {"$in": ids}},
                {"$set": {'status': STATUS['pending']}})

        return flags

    def update_flags(self, flags=[]):
        # we will need to generate some bulk queries now for mongodb
        changes = {}
        for status in STATUS.itervalues():
            changes[status] = []

        # for each changed status we will update
        for flag in flags:
            changes[flag["status"]].append(flag["_id"])

        for status, flags in changes.items():
            # if there are flags to upate, do a bulk update on mongodb
            if flags:
                self.flagz.update_many(
                    {"_id": {"$in": flags}}, {"$set": {"status": status}})

    def insert_flags(self, team, service, flags):
        result = self.flagz.insert_many(
            [{
                'flag': i,
                'team': team,
                'service': service,
                'status': STATUS['unsubmitted'],
            } for i in flags])

        print result
