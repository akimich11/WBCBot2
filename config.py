import yaml


with open('assets/rus.yaml') as f:
    phrases = yaml.load(f, Loader=yaml.FullLoader)


TOKEN = '1471952931:AAFp0m8i76vG0urF-Q8OeGfQeCmJCdKaoMs'
HOSTNAME = 'eu-cdbr-west-01.cleardb.com'
DATABASE_NAME = 'heroku_76a392e231013c5'
USER = 'b9964e3916d7d5'
PASSWORD = '31ccb670'
AKIM_ID = 270241310
ACCEPTED_FORMATS = ("jpg", "jpeg", "png")
