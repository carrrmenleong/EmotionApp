import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))
MAIL_USERNAME = os.environ['MAIL_USERNAME']
print(MAIL_USERNAME)
print(os.getcwd())