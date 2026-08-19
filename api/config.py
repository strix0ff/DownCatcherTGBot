from os import (
    getenv
)

from dotenv import (
    load_dotenv
)

load_dotenv()

PORT = int(getenv('APIPORT'))
DBNAME = getenv('DBNAME')
APIKEY = getenv('APIKEY')