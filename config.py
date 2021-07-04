import os
import yaml
from urllib.parse import urlparse

with open('assets/rus.yaml') as f:
    phrases = yaml.load(f, Loader=yaml.FullLoader)

TOKEN = os.environ['BOT_TOKEN']

url = urlparse(os.environ['DATABASE_URL'])
USER = url.username
PASSWORD = url.password
HOSTNAME = url.hostname
DATABASE_NAME = os.environ['DATABASE_NAME']

AKIM_ID = int(os.environ['AKIM_ID'])
ACCEPTED_FORMATS = ("jpg", "jpeg", "png")
