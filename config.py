import os
import yaml
from urllib.parse import urlparse

with open('assets/ru_RU.yaml') as f:
    phrases = yaml.load(f, Loader=yaml.FullLoader)

# TOKEN = os.environ['BOT_TOKEN']
#
# url = urlparse(os.environ['DATABASE_URL'])
# USER = url.username
# PASSWORD = url.password
# HOSTNAME = url.hostname
# DATABASE_NAME = os.environ['DATABASE_NAME']
#
# AKIM_ID = int(os.environ['AKIM_ID'])

TOKEN = '1165511829:AAHAp5NsBFMvbYzNjTzeU0Esl0nDS-XYBXY'
HOSTNAME = 'eu-cdbr-west-01.cleardb.com'
DATABASE_NAME = 'heroku_76a392e231013c5'
USER = 'b9964e3916d7d5'
PASSWORD = '31ccb670'
AKIM_ID = 270241310
ACCEPTED_FORMATS = ("jpg", "jpeg", "png")
