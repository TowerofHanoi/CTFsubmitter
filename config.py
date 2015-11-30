config = {
    "debug": True,
    "flags_db": "flagsdb",
    "flag_regex": "\w{31}=",
    "worker_sleep_time": 1,
    "mongodb": {
        "host": "***REMOVED***",
        "port": 27017,
        "log_size": 500*1024
    },
    "flags_bulk_num": 80,
    "expireFlagAfter": 60*30

}

STATUS = {
    "rejected": 0,
    "accepted": 1,
    "old": 2,
    "unsubmitted": 3,
    "pending": 4,
    "submitted": 5
}