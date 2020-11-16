"""
Constants module.
"""

import os

# Test mode
try:
    TEST_MODE = os.environ["ENS_TEST_MODE"].lower() == 'true'
except:
    TEST_MODE = False

# Verbose level
try:
    CONST_VERBOSE_LEVEL = int(os.environ["ENS_VERBOSE_LEVEL"])
except:
    CONST_VERBOSE_LEVEL = 2

# Connection strings
SQL_ENGINE = "postgresql"

if TEST_MODE:
    print("!!! EduNotice is running TEST MODE !!!")

    SQL_USER = "postgres"
    SQL_PASSWORD = ""
    SQL_HOST = "localhost"
    SQL_PORT = "5432"
    SQL_DBNAME = "edutestdb"
else:
    SQL_USER = os.environ["ENS_SQL_USER"]
    SQL_PASSWORD = os.environ["ENS_SQL_PASS"]
    SQL_HOST = os.environ["ENS_SQL_HOST"]
    SQL_PORT = os.environ["ENS_SQL_PORT"]
    SQL_DBNAME = os.environ["ENS_SQL_DBNAME"].strip().lower()

SQL_DEFAULT_DBNAME = "postgres"
SQL_TEST_DBNAME1 = "edutestdb1"
SQL_TEST_DBNAME2 = "edutestdb2"
SQL_TEST_DBNAME3 = "edutestdb3"
SQL_TEST_DBNAME4 = "edutestdb4"
SQL_TEST_DBNAME5 = "edutestdb5"

SQL_CONNECTION_STRING = "%s://%s:%s@%s:%s" % (
    SQL_ENGINE,
    SQL_USER,
    SQL_PASSWORD,
    SQL_HOST,
    SQL_PORT,
)

SQL_CONNECTION_STRING_DEFAULT = "%s/%s" % (SQL_CONNECTION_STRING, SQL_DEFAULT_DBNAME)

SQL_CONNECTION_STRING_DB = "%s/%s" % (SQL_CONNECTION_STRING, SQL_DBNAME)

# SendGrid
SG_FROM_EMAIL = os.environ.get('ENS_FROM_EMAIL')
SG_SUMMARY_RECIPIENTS = os.environ.get('ENS_SUMMARY_RECIPIENTS')
SG_API_KEY = os.environ.get('ENS_EMAIL_API')
try:
    SG_TEST_EMAIL = TEST_MODE and os.environ["ENS_TEST_EMAIL_API"].lower() == 'true'
except:
    SG_TEST_EMAIL = False

__email_excl = os.environ.get('ENS_EMAIL_EXCL')
if type(__email_excl) is str:
    SG_EMAIL_EXCL = [x.strip() for x in __email_excl.split(',')]
else:
    SG_EMAIL_EXCL = None

CONST_EMAIL_SUBJECT_NEW = "Azure subscription registred"
CONST_EMAIL_SUBJECT_UPD = "Azure subscription updated"
CONST_EMAIL_SUBJECT_CANCELLED = "Azure subscription cancelled"
CONST_EMAIL_SUBJECT_EXPIRE = "Azure subscription expires in"
CONST_EMAIL_SUBJECT_USAGE = "Azure subscription's utilisation &#8805; "

SG_TEST_FROM = os.environ.get('ENS_TEST_FROM_EMAIL')
SG_TEST_TO = os.environ.get('ENS_TEST_TO_EMAIL')

try:
    SG_EMAIL_DISABLE = os.environ["ENS_EMAIL_DISABLE"].lower() == 'true'
except:
    SG_EMAIL_DISABLE = False

# DB Constants
COURSES_TABLE_NAME = "course"
LABS_TABLE_NAME = "lab"
SUBSCRIPTIONS_TABLE_NAME = "subscription"
DETAILS_TABLE_NAME = "details"
LOGS_TABLE_NAME = "logs"

ID_COL_NAME = "id"

# Log codes
CONST_LOG_CODE_SUCCESS = 0 # The operation completed successfully.

# Notification codes
CONST_EXPR_CODE_0 = 0
CONST_EXPR_CODE_1 = 1
CONST_EXPR_CODE_7 = 7
CONST_EXPR_CODE_30 = 30

CONST_USAGE_CODE_50 = 50
CONST_USAGE_CODE_75 = 75
CONST_USAGE_CODE_90 = 90
CONST_USAGE_CODE_95 = 95

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

CONST_SUB_CANCELLED = "Canceled"

# paths
CONST_TEST_FOLDER = "tests"
CONST_DATA_FOLDER = "data"

CONST_TEST1_FILENAME = "ec_output_1.csv"
CONST_TEST2_FILENAME = "ec_output_2.csv"
CONST_TEST3_FILENAME = "ec_output_3.csv"
CONST_TEST4_FILENAME = "ec_output_4.csv"
CONST_TEST5_FILENAME = "ec_output_5.csv"
CONST_TEST6_FILENAME = "ec_output_6.csv"
CONST_TEST7_FILENAME = "ec_output_7.csv"
CONST_TEST8_FILENAME = "ec_output_8.csv"
CONST_TEST9_FILENAME = "ec_output_9.csv"
CONST_TEST10_FILENAME = "ec_output_10.csv"
CONST_TEST11_FILENAME = "ec_output_11.csv"
CONST_TEST12_FILENAME = "ec_output_12.csv"

CONST_TEST_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "..", "..", CONST_TEST_FOLDER
    )
)

CONST_TEST_DIR_DATA = os.path.join(CONST_TEST_DIR, CONST_DATA_FOLDER)
