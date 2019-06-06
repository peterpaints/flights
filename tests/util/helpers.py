import datetime
import json


class JsonEncoderWithDatetime(json.JSONEncoder):
    """Convert datetime.date objects to string."""

    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super(JsonEncoderWithDatetime, self).default(obj)
