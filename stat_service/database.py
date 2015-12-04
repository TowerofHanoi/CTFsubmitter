import motor

client = motor.MotorClient('192.168.56.8', 27017)
db = client['submitter']
logs = db['logs']
stats = db['statistics']
