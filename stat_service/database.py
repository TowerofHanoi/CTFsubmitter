import motor

client = motor.MotorClient('***REMOVED***', 27017)
db = client['submitter']
logs = db['logs']
stats = db['statistics']
