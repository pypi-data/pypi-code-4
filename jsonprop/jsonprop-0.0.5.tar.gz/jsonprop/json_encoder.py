import json

class JsonObjectEncoder(json.JSONEncoder):
    """JSON encoder that will serialize JsonObject types"""
    def default(self, obj):
        try:
            return obj._to_json_dict()
        except Exception as e:
            print e
            return json.JSONEncoder.default(self, obj)
