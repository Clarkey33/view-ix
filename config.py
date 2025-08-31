#from dotenv import dotenv_values
from dotenv import load_dotenv
import os

#env_tokens = dotenv_values('.env')

load_dotenv()

CACHE_DURATION_SECONDS = int(os.getenv('CACHE_DURATION_SECONDS'))
LAST_CACHE_TIME = float(os.getenv('LAST_CACHE_TIME'))
BASE_URL = os.getenv('BASE_URL')
#BASE_URL_INJ = env_tokens.get('BASE_URL_INJ')

