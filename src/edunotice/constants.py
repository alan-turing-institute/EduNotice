"""
Constants module.
"""

import os

# Test mode
try:
    TEST_MODE = os.environ["ENS_TEST_MODE"].lower() == 'true'
except:
    TEST_MODE = False

# DB Constants
COURSES_TABLE_NAME = "course"
LABS_TABLE_NAME = "lab"
SUBSCRIPTIONS_TABLE_NAME = "subscription"
DETAILS_TABLE_NAME = "details"
LOGS_TABLE_NAME = "logs"

ID_COL_NAME = "id"

# Log codes
CONST_LOG_CODE_SUCCESS = 0 # The operation completed successfully.

# Connection strings
SQL_ENGINE = "postgresql"
SQL_USER = os.environ["ENS_SQL_USER"]
SQL_PASSWORD = os.environ["ENS_SQL_PASS"]
SQL_HOST = os.environ["ENS_SQL_HOST"]
SQL_PORT = os.environ["ENS_SQL_PORT"]
SQL_DBNAME = os.environ["ENS_SQL_DBNAME"].strip().lower()
SQL_DEFAULT_DBNAME = "postgres"
SQL_TEST_DBNAME1 = "edutestdb1"
SQL_TEST_DBNAME2 = "edutestdb2"

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
CONST_PD_COL_COURSE_NAME = "Course name"
CONST_PD_COL_LAB_NAME = "Lab name"
CONST_PD_COL_HANDOUT_NAME = "Handout name"
CONST_PD_COL_HANDOUT_BUDGET = "Handout budget"
CONST_PD_COL_HANDOUT_CONSUMED = "Handout consumed"
CONST_PD_COL_HANDOUT_STATUS = "Handout status"
CONST_PD_COL_SUB_ID = "Subscription id"
CONST_PD_COL_SUB_NAME = "Subscription name"
CONST_PD_COL_SUB_STATUS = "Subscription status"
CONST_PD_COL_SUB_EXPIRY_DATE = "Subscription expiry date"
CONST_PD_COL_SUB_USERS = "Subscription users"
CONST_PD_COL_CRAWL_TIME_UTC = "Crawl time utc"

# paths
CONST_TEST_FOLDER = "tests"
CONST_DATA_FOLDER = "data"

CONST_TEST1_FILENAME = "ec_output_1.csv"
CONST_TEST2_FILENAME = "ec_output_2.csv"
CONST_TEST3_FILENAME = "ec_output_3.csv"

CONST_TEST_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", CONST_TEST_FOLDER
    )
)

CONST_TEST_DIR_DATA = os.path.join(CONST_TEST_DIR, CONST_DATA_FOLDER)
