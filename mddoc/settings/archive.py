from .default import *

ARCHIVE = True

SESSION_COOKIE_NAME = "archive_sessionid"

DATABASES['default']['NAME'] = BASE_DIR / 'db.archive.sqlite3'
DATABASES['archive']['NAME'] = BASE_DIR / 'db.dummy.sqlite3'