import os
import uuid
from time import time

from cassandra.cqlengine import connection
from flask import request, make_response
from flask_restful import Resource
from google.cloud import storage
from google.cloud.storage import Blob
from google.oauth2 import service_account

from conf.config import ASSETS_BUCKET, IMAGE_EXPIRATION_SECONDS, GOOGLE_CREDENTIALS, CASSANDRA_HOSTS, USER_KEYSPACE
from model.asset import AssetByAssetName, AssetByUserId
from service.common import get_user_id_from_jwt


class Image(Resource):
    def post(self):
        user_id = get_user_id_from_jwt()
        if not user_id:
            return make_response("Missing user id", 500)

        image_file = request.files.get('image')
        if not image_file:
            return make_response("Missing image file", 500)

        # save image
        filename_first, file_extension = os.path.splitext(image_file.filename)
        filename = filename_first + "." + str(uuid.uuid4()) + file_extension

        self._upload_asset(filename, image_file)
        self._save_to_db(filename, user_id)

        return {
            "image_name": filename,
            "image_url": self._get_image_signed_url(filename)
        }

    @staticmethod
    def _upload_asset(filename, image_file):
        # storage
        if GOOGLE_CREDENTIALS:
            google_credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS)
        else:
            google_credentials = None
        client = storage.Client(credentials=google_credentials)
        bucket = client.get_bucket(ASSETS_BUCKET)
        blob = Blob(filename, bucket)
        blob.upload_from_file(image_file)

    @staticmethod
    def _get_image_signed_url(image_file):

        if GOOGLE_CREDENTIALS:
            google_credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDENTIALS)
        else:
            google_credentials = None

        client = storage.Client(credentials=google_credentials)
        bucket = client.get_bucket(ASSETS_BUCKET)
        blob = Blob(image_file, bucket)
        signed_url = blob.generate_signed_url(int(time() + IMAGE_EXPIRATION_SECONDS))
        return signed_url

    @staticmethod
    def _save_to_db(filename, user_id):
        connection.setup(hosts=CASSANDRA_HOSTS, default_keyspace=USER_KEYSPACE)
        AssetByAssetName.create(
            asset_name=filename,
            user_id=user_id
        )

        AssetByUserId.create(
            asset_name=filename,
            user_id=user_id
        )


class GetImageUrl(Image):
    def get(self, image_name):
        return {
            "images": {
                image_name: self._get_image_signed_url(image_name)
            }
        }


class GetImageUrlBulk(Image):
    def post(self):
        data = request.get_json(silent=True)

        image_names = data.get("images")
        if not len(image_names):
            return make_response("You must send the list of images")

        images = {}
        for image_name in image_names:
            images[image_name] = {
                "image_url": self._get_image_signed_url(image_name)
            }
        return {
            "images": images
        }
