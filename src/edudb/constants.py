
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

# pandas dataframe column names
CONST_PD_COL_COURSE_NAME = 'Course name'
CONST_PD_COL_SUB_ID = 'Subscription id'
CONST_PD_COL_CRAWL_TIME_UTC = 'Crawl time utc'

# ['Lab name', 
# 'Handout name', 'Handout budget', 'Handout consumed', 
# 'Handout status', 'Subscription name', 'Subscription id', 
# 'Subscription status', 'Subscription expiry date', 
# 'Subscription users', 'Crawl time utc']


# paths
CONST_TEST_FOLDER = "tests"
CONST_DATA_FOLDER = "data"

CONST_TEST1_FILENAME = "ec_output_1.csv"

CONST_TEST_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", CONST_TEST_FOLDER)
)

CONST_TEST_DIR_DATA = os.path.join(CONST_TEST_DIR, CONST_DATA_FOLDER)
