from json import JSONEncoder
from datetime import datetime
from bson import ObjectId


class DateEncoder(JSONEncoder):
    """JSON serializer for objects not serializable by default json code"""
    def default(self, obj):
        if isinstance(obj, datetime):
            encoded = obj.strftime("%b %d %y - %H:%M:%S")
        elif isinstance(obj, ObjectId):
            encoded = str(obj)
        else:
            encoded = JSONEncoder.default(self, obj)
        return encoded

date_encoder = DateEncoder()
