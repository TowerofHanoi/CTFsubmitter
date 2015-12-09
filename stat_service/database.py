import motor

client = motor.MotorClient('localhost', 27017)
db = client['submitter']
logs = db['logs']
stats = db['statistics']
