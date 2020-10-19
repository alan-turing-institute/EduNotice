
"""
Constants module.
"""

import os

# DB Constants
COURSES_TABLE_NAME = "course"
LABS_TABLE_NAME = "lab"
SUBSCRIPTIONS_TABLE_NAME = "subscription"
DETAILS_TABLE_NAME = "details"

ID_COL_NAME = "id"

# Connection strings
SQL_ENGINE = "postgresql"
SQL_USER = os.environ["EDB_SQL_USER"]
SQL_PASSWORD = os.environ["EDB_SQL_PASS"]
SQL_HOST = os.environ["EDB_SQL_HOST"]
SQL_PORT = os.environ["EDB_SQL_PORT"]
SQL_DBNAME = os.environ["EDB_SQL_DBNAME"].strip().lower()
SQL_DEFAULT_DBNAME = "postgres"

SQL_CONNECTION_STRING = "%s://%s:%s@%s:%s" % (
    SQL_ENGINE,
    SQL_USER,
    SQL_PASSWORD,
    SQL_HOST,
    SQL_PORT,
)

SQL_CONNECTION_STRING_DEFAULT = "%s/%s" % (SQL_CONNECTION_STRING, SQL_DEFAULT_DBNAME)
SQL_CONNECTION_STRING_DB = "%s/%s" % (SQL_CONNECTION_STRING, SQL_DBNAME)