#/backend/app/core/config.py

import os
from google.cloud import secretmanager

#Creating the secret manager client
client = secretmanager.SecretManagerServiceClient()

#Creating our name reference
name = f"projects/{GOOGLE_PROJECT_ID}/secrets/{GOOGLE_SECRET_NAME}/versions/latest"

#########################
# DB connection config from db.py
DB_DRIVER = 'PostgreSQL Unicode'
DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_USER = os.getenv('DB_USER')
##DB_PASSWORD = os.getenv('DB_PASSWORD')
GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
GOOGLE_SECRET_NAME = os.getenv('GOOGLE_SECRET_NAME')

######################
# Accessing the secrets
######################
response = client.access_secret_version(
    request={"name": name}
)
DB_PASSWORD = response.payload.data.decode("UTF-8")

######################
# Global pool connnection config from db.py
######################
POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))

######################
# environment variables to detect if we are in prod, dev, etc
ENV = os.getenv("ENV", "development")

IS_TEST = ENV == "test"