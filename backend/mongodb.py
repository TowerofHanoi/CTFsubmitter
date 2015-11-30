from pymongo import MongoClient, errors, IndexModel, ASCENDING
from base import BaseBackend
from config import config
from submitter import STATUS
from datetime import datetime
from itertools import izip_longest


class MongoBackend(BaseBackend):

    def _create_collections(self):
        # create the capped collection to contain flags
        try:
            self.db.create_collection("flag_list")
            self.db.create_collection('submissions')
            #         capped=True,
            #         size=config["mongodb"].get(
            #             "capped_collection_size", 500*1024*1024)
            #     )
            # insert a dummy document or await will fail on empty collection
            # self.db.flagz.insert({
            #     "status": 1, "service": "dummy",
            #     "insertedAt": datetime.utcnow(), "flag": "init", "team": 0})

        except errors.CollectionInvalid:
            # the collection already exists, an error happened,
            # let's scan for the tail of the collection
            self.db.find({})

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
        # index3 = IndexModel(
        #     [("insertedAt", ASCENDING)],
        #     expiresAfter=config.get("expireFlagAfter"),
        #     name="expireflags")

        self.flag_list.create_indexes([index1, index2])

    def _connect(self):
        self.client = MongoClient(
            config['mongodb']['host'],
            config['mongodb']['port'])

        self._create_collections()
        self._create_indexes()

        self.db = self.client["submitter"]
        self.flag_list = self.db['flag_list']  # contains the iterable of flags
        self.submissions = self.db['submissions']
        # self.global_flagz = self.db["global_flagz"]
        # contains every single flag to check for

    def _close(self):
        self.client.close()

    def get_task(self, N=None):
        # find an unsubmitted block of flags
        submission = self.submissions.find_one_and_update(
                {'status': STATUS['unsubmitted']},
                {'$set': {'status': STATUS['pending']}})

        flags = self.flag_list.find(
            {'_id': {'$in': submission['flags']}})
        submission['flags'] = flags  # client-side join
        return submission

    def update_flags(self, submission, status):

        # create a new set of unsubmitted flags for the
        # service if some submissions failed, we will need to retry
        # TODO: set a max number of retries x flag

        unsubmitted_flags = [
            f[0] for f in izip_longest(
                        submission['flags'], status,
                        fillvalue=STATUS['unsubmitted'])
            if f[1] == STATUS['unsubmitted']]

        self.submissions.find_one_and_update(
            {'service': submission['service'],
                'status': STATUS["unsubmitted"]},
            {"$addToSet": {'flags', {"$each": unsubmitted_flags}}},
            upsert=True
        )

        # and set the old submission as "submitted"
        self.submissions.update_one(
            {'_id': submission['_id']},
            {'$set': {'status': STATUS["submitted"]}})

    def insert_flags(self, team, service, flags):

        # insert into a list of flags submitted recently (x service)
        result = self.flag_list.insert_many([
            [{'service': service,
                'team': team,
                'flag': flag,
                "insertedAt": datetime.utcnow()}] for flag in flags
            ])

        # insert into bulk blocks of flags x per service
        self.submissions.find_one_and_update(
            {'service': service,
                'status': STATUS["unsubmitted"]},
            {"$addToSet": {'flags', {"$each": result}}},
            upsert=True
        )
