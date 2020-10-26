"""
Test notifications.py module
"""

import os
import pandas as pd

from sqlalchemy import create_engine

from edunotice.ingress import update_edu_data

from edunotice.notifications import (
   summary,
)

from edunotice.constants import (
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME2
)

# good data
file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
eduhub_df1 = pd.read_csv(file_path)

ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME2))

def test_summary():

    # real data
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    succes, error, lab_dict, sub_dict, sub_new_list, sub_update_list = update_edu_data(ENGINE, eduhub_df)

    assert succes, error
    assert len(sub_new_list) == 2
    assert len(sub_update_list) == 0

    succes, error, html_content = summary(lab_dict, sub_dict, sub_new_list, sub_update_list)

    assert succes, error

    print(html_content)

    assert False