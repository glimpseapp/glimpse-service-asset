import time
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.util import datetime_from_timestamp


def date_now():
    return datetime_from_timestamp(time.time())


class AssetByUserId(Model):
    user_id = columns.Text(primary_key=True)
    asset_name = columns.Text()
    time = columns.DateTime(default=date_now)

    def to_object(self):
        return {
            'user_id': str(self.sender_id),
            'asset_name': str(self.receiver_id),
            'time': self.time.isoformat()
        }


class AssetByAssetName(Model):
    asset_name = columns.Text(primary_key=True)
    user_id = columns.Text()
    time = columns.DateTime(default=date_now)

    def to_object(self):
        return {
            'user_id': str(self.sender_id),
            'asset_name': str(self.receiver_id),
            'time': self.time.isoformat()
        }