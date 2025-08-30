from dotenv import dotenv_values
env_tokens = dotenv_values('.env')



CACHE_DURATION_SECONDS = int(env_tokens.get('CACHE_DURATION_SECONDS'))
LAST_CACHE_TIME = float(env_tokens.get('LAST_CACHE_TIME'))
BASE_URL = env_tokens.get('BASE_URL')
BASE_URL_INJ = env_tokens.get('BASE_URL_INJ')

