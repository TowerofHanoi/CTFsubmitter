from pymongo import MongoClient, errors, IndexModel, ASCENDING
from base import BaseBackend
from config import config
from submitter import STATUS
from datetime import datetime


class MongoBackend(BaseBackend):

    def _create_indexes(self):

        # quick querying for status
        index1 = IndexModel([("status", ASCENDING)], name="status")
        # ensure unique flags x service x team
        index2 = IndexModel([
            ("flag", ASCENDING),
            ("service", ASCENDING),
            ("team", ASCENDING)],
            unique=True,
            name="uniqueflags")
        # index3 = IndexModel(
        #     [("insertedAt", ASCENDING)],
        #     expiresAfter=config.get("expireFlagAfter"),
        #     name="expireflags")

        self.flagz.create_indexes([index1, index2])

    def _connect(self):
        self.client = MongoClient(
            config['mongodb']['host'],
            config['mongodb']['port'])
        self.db = self.client["submitter"]
        self.flagz = self.db['flagz']
        self._create_indexes()

    def _close(self):
        self.client.close()

    def get_flags(self, N=None):
        # flags = self.flagz.aggregate()
        if not N:
            N = config.get("flags_bulk_num", 80)

        cursor = self.flagz.find({'status': STATUS['unsubmitted']}).limit(N)

        if cursor:
            flags = []
            ids = []
            for flag in cursor:
                flags.append(flag)
                ids.append(flag["_id"])
            self.flagz.update_many(
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
        # should we want an id based on the time submitted
        # we can use the submit time and loose some precision (~30mins)
        # thus generating a nice hash :)
        # packed binary values + sha1 can be used

        try:
            self.flagz.insert_many(
                [{
                    'flag': i,
                    'team': team,
                    'service': service,
                    'status': STATUS['unsubmitted'],
                    'insertedAt': datetime.utcnow()
                } for i in flags],
                ordered=False)
        except errors.BulkWriteError:
            # ignore duplicate keys
            pass
