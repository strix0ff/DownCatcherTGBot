from os import (
    getenv
)

from dotenv import (
    load_dotenv
)

load_dotenv()

BOTTOKEN = getenv('BOTTOKEN')
ADMINID = getenv('ADMIN_USERID')
APIKEY = getenv('APIKEY')
APIPORT = getenv('APIPORT')