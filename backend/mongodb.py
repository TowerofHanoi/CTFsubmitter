from pymongo import MongoClient, errors, IndexModel, ASCENDING
from base import BaseBackend
from config import config, STATUS, rSTATUS
from datetime import datetime
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
        self.db.log.insert({'msg': message})

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
                    "log_size", 500*1024)
                )
            # insert a dummy document or await will fail on empty collection
            # self.db.flagz.insert({
            #     "status": 1, "service": "dummy",
            #     "insertedAt": datetime.utcnow(), "flag": "init", "team": 0})

        except errors.CollectionInvalid:
            pass
        finally:
            self.flag_list = self.db['flag_list']  # flags
            self.submissions = self.db['submissions']  # task
            self.stats = self.db['statistics']  # stats
            self.logs = self.db['logs']

    def _create_indexes(self):

        # quick querying for status
        index1 = IndexModel(
            [("status", ASCENDING), ("service", ASCENDING)], name="status")
        # ensure unique flags x service x team
        index2 = IndexModel([
            ("flag", ASCENDING),
            ("team", ASCENDING),
            ("service", ASCENDING)],
            name="uniqueflags")
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

        # create a new set of unsubmitted flags for the
        # service if some submissions failed, we will need to retry
        # TODO: set a max number of retries x flag
        # let's add some stats :)

        stats = {'ip': submission.get('ip')}
        for k, v in Counter(status).iteritems():
            stats[rSTATUS[k]] = v
        self.stats.insert(stats)

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

        # insert into a list of flags submitted recently (x service)
        result = self.flag_list.insert_many([
            {'service': service,
                'team': team,
                'flag': flag,
                'insertedAt': datetime.utcnow(),
                'ip': ip,
                'name': name} for flag in flags
            ])

        # no race conditions since we use the results of insertion!
        # no flag can be submitted twice!

        # insert into bulk blocks of flags x per service
        self.submissions.find_one_and_update(
            {'service': service,
                'status': STATUS['unsubmitted']},
            {'$addToSet': {'flags': {'$each': result.inserted_ids}},
             '$set': {'ip': ip, 'name': name}},
            upsert=True
        )
