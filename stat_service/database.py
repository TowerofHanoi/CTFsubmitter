import motor

client = motor.MotorClient('mongo-dev', 27017)
db = client['submitter']
logs = db['logs']
stats = db['statistics']
