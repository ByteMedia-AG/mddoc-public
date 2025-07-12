from .default import *

TEST = True

SESSION_COOKIE_NAME = "test_sessionid"

DATABASES['default']['NAME'] = BASE_DIR / 'db.test.sqlite3'
DATABASES['archive']['NAME'] = BASE_DIR / 'db.archive.sqlite3'