from datetime import datetime as dt
from dotenv import load_dotenv
import os

VERSION = 'V0.2.5'
NAME = 'NovusEdge'
FNAME = 'Bearhouse Capital'
DATETIME = dt.now().strftime('%Y-%m-%d %H:%M:%S.%f')
AUTHOR = 'Sonny Holman'

load_dotenv()

DBNAME = os.getenv('DB_NAME')
DBUSER = os.getenv('DB_USER')
DBPASS = os.getenv('DB_PASS')
DBHOST = os.getenv('DB_HOST')
DBPORT = os.getenv('DB_PORT')
PG_EXE = os.getenv('PG_EXE')