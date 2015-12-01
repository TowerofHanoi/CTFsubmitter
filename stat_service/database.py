import motor
from config import config

mongo_cfg = config['mongodb']

client = motor.MotorClient(
    mongo_cfg['host'], mongo_cfg['port'])

db = client[client['submitter']]
logs = db['logs']
