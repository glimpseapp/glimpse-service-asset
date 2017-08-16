import os

from time import time

HTTP_PORT = os.getenv("HTTP_PORT", 5000)
HTTP_HOST = os.getenv("HTTP_HOST", "0.0.0.0")

# this can be an array of IPs
CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOSTS", None)
if isinstance(CASSANDRA_HOSTS, str):
    CASSANDRA_HOSTS = CASSANDRA_HOSTS.split(',')

USER_KEYSPACE = "asset"

ASSETS_BUCKET = os.getenv("ASSETS_BUCKET", "glimpse-asset")
IMAGE_EXPIRATION_TIME = int(time() + os.getenv("IMAGE_EXPIRATION_TIME", 3600))

GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS", None)