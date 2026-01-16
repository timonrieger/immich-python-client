# Source - https://stackoverflow.com/a
# Posted by IVI
# Retrieved 2026-01-16, License - CC BY-SA 3.0

import json
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)
