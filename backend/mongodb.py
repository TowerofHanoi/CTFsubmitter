from pymongo import (
    MongoClient, errors, IndexModel, ASCENDING)
from bson import ObjectId
from base import BaseBackend
from config import config, STATUS, rSTATUS
from datetime import datetime
from time import mktime
from itertools import izip_longest
from collections import Counter


class MongoBackend(BaseBackend):

    def cold_restart(self):
        """ this will set all the pending tasks to submitted """
        while(self.submissions.find_one_and_update(
                {'status': STATUS['pending']},
                {'$set': {'status': STATUS['unsubmitted']}})):
            pass

    def insert_logmsg(self, message):
        """Insert a log message inside mongodb capped collection"""
        self.logs.insert(message)

    def _create_collections(self):
        # create the capped collection to contain flags
        try:
            self.db.create_collection('statistics')
            self.db.create_collection('flag_list')
            self.db.create_collection('submissions')
            self.db.create_collection(
                'logs',
                capped=True,
                size=config["mongodb"].get(
                    "log_size", 500*1024))

        except errors.CollectionInvalid:
            pass
        finally:
            self.flag_list = self.db['flag_list']  # flags
            self.submissions = self.db['submissions']  # task
            self.stats = self.db['statistics']  # stats
            self.team_stats = self.db['serv_stats']  # stats
            self.service_stats = self.db['team_stats']  # stats
            self.logs = self.db['logs']

    def _create_indexes(self):

        # quick querying for status
        index1 = IndexModel(
            [("status", ASCENDING), ("service", ASCENDING)], name="status")
        # ensure unique flags x service x team
        index2 = IndexModel([
            ("flag", ASCENDING),
            ("team", ASCENDING),
            ("service", ASCENDING),
            ("insertedAt", ASCENDING)],
            name="uniqueflags",
            unique=True)

        index3 = IndexModel([('name', ASCENDING)])
        index4 = IndexModel([('ip', ASCENDING)])
        #     [("insertedAt", ASCENDING)],
        #     expiresAfter=config.get("expireFlagAfter"),
        #     name="expireflags")

        self.flag_list.create_indexes([index1, index2, index3, index4])
        self.submissions.create_indexes([index3, index4])
        self.logs.create_index([('insertedAt', ASCENDING)])

    def _connect(self):
        self.client = MongoClient(
            config['mongodb']['host'],
            config['mongodb']['port'])

        self.db = self.client["submitter"]

        self._create_collections()
        self._create_indexes()

        # self.global_flagz = self.db["global_flagz"]
        # contains every single flag to check for

    def _close(self):
        self.client.close()

    def get_task(self, N=None):
        # find an unsubmitted block of flags
        submission = self.submissions.find_one_and_update(
                {'status': STATUS["unsubmitted"]},
                {'$set': {'status': STATUS["pending"]}})

        if not submission:
            return None

        flags = list(self.flag_list.find(
            {'_id': {'$in': submission['flags']}}))
        submission['flags'] = flags  # client-side join
        return submission

    def update_flags(self, submission, status):

        if not submission['flags']:
            raise ValueError("Something strange happened! Empty flag set!")

        stats = {}
        for k, v in Counter(status).iteritems():
            stats[rSTATUS[k]] = v

        self.stats.update_one(
            {'_id': ('user_%s' % submission.get('ip'))},
            {'$set': {'name': submission.get('name', "")},
             '$inc': stats},
            upsert=True)

        unsubmitted_flags = [
            f[0] for f in izip_longest(
                        submission['flags'], status,
                        fillvalue=STATUS["unsubmitted"])
            if f[1] == STATUS["unsubmitted"]]

        self.submissions.update_one(
            {'_id': submission['_id']},
            {'$set': {'status': STATUS["submitted"]}})

        if unsubmitted_flags:
            self.submissions.update_one(
                {'service': submission['service'],
                    'status': STATUS["unsubmitted"]},
                {"$addToSet": {'flags': {"$each": unsubmitted_flags}}},
                upsert=True)

    def insert_flags(self, team, service, flags, name, ip):

        x = config.get("mem_rounds", 2)
        date = datetime.utcnow()
        date = int(mktime(date.timetuple()))
        date /= 60*x
        date *= 60*x  # loose some precision (2 min)
        date = datetime.fromtimestamp(date)

        inserted_ids = []

        def gen():
            """A generator that validates documents and handles _ids."""
            for flag in flags:
                document = {
                    '_id': ObjectId(),
                    'service': service,
                    'team': team,
                    'flag': flag,
                    'insertedAt': date,
                    'ip': ip,
                    'name': name}
                inserted_ids.append(document["_id"])
                yield document

        blk = self.flag_list.initialize_unordered_bulk_op()

        [blk.insert(doc) for doc in gen()]

        try:
            result = blk.execute()
        except errors.BulkWriteError as bwe:

            for insert_err in bwe.details['writeErrors']:
                try:
                    inserted_ids.remove(insert_err['op']['_id'])
                except ValueError:
                    pass
            result = bwe.details

        result['inserted_details'] = inserted_ids

        # no race conditions since we use the results of insertion!
        # no flag can be submitted twice!

        # insert into bulk blocks of flags x per service
        if inserted_ids:
            self.submissions.find_one_and_update(
                {'service': service,
                    'status': STATUS['unsubmitted']},
                {'$addToSet': {'flags': {'$each': inserted_ids}},
                 '$set': {'ip': ip, 'name': name}},
                upsert=True)

        # omg that sucks! :D
        blk = self.stats.initialize_unordered_bulk_op()

        blk.find({'_id': '_total'}).upsert().update(
            {'$inc': {
                'total_submitted': len(flags),
                'total_inserted': len(inserted_ids)}})

        # add service stat
        blk.find({'_id': ('service_%s' % service)}).upsert().update(
            {'$inc': {
                'total_submitted': len(flags),
                'total_inserted': len(inserted_ids)}})

        # add team stat
        blk.find({'_id': ('team_%s' % team)}).upsert().update(
            {'$inc': {
                'total_submitted': len(flags),
                'total_inserted': len(inserted_ids)}})

        # add user stat
        blk.find({'_id': ('user_%s' % ip)}).upsert().update(
            {'$inc': {
                'total_submitted': len(flags),
                'total_inserted': len(inserted_ids)}})

        blk.execute()

        return result
