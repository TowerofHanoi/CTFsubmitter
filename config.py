config = {
    "debug": True,
    "flags_db": "flagsdb",
    "flag_regex": "\w{31}=",
    "worker_sleep_time": 5,
    "mongodb": {
        "host": "andrototal-dev",
        "port": 27017,
        "log_size": 500*1024
    },
    # the number of rounds to check against for the same flag to appear
    "mem_rounds": 2,
    "expireFlagAfter": 60*30,
    "token": "FDwc2R9UN7jA6j2H",
    "email": "towerofhanoictf@gmail.com"
}

STATUS = {
    "rejected": 0,
    "accepted": 1,
    "old": 2,
    "unsubmitted": 3,
    "pending": 4,
    "submitted": 5
}

rSTATUS = {
    0: "rejected",
    1: "accepted",
    2: "old",
    3: "unsubmitted",
    4: "pending",
    5: "submitted"
}
