"""
Test notifications.py module
"""

import os
import pandas as pd

from sqlalchemy import create_engine, func

from edunotice.ingress import (
    update_edu_data,
    get_latest_log_timestamp,
)

from edunotice.notifications import (
   summary,
)

from edunotice.constants import (
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
    CONST_TEST2_FILENAME,
    CONST_TEST3_FILENAME,
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME2
)

from edunotice.structure import LogsClass

from edunotice.db import (
    session_open,
    session_close,
)

# good data
file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
eduhub_df1 = pd.read_csv(file_path)

ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME2))

def test_summary():

    ################### UPDATE 1

    # get the latest log timestamp value
    succes, error, latest_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert succes, error
    assert latest_timestamp_utc is None
    
    # real data
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    succes, error, lab_dict, sub_dict, sub_new_list, sub_update_list, success_timestamp_utc = update_edu_data(ENGINE, eduhub_df)

    assert succes, error
    assert len(sub_new_list) == 2
    assert len(sub_update_list) == 0

    # checking if the log message was created
    session = session_open(ENGINE)
    query_cnt = session.query(func.count(LogsClass.id)).scalar()
    session_close(session)
    assert query_cnt == 1

    # no changes
    succes, error, html_content = summary(lab_dict, sub_dict, [], [], 
        latest_timestamp_utc, success_timestamp_utc)

    assert succes, error
    assert len(html_content) == 1295

    # 2 new subscriptions
    succes, error, html_content = summary(lab_dict, sub_dict, sub_new_list, sub_update_list, 
        latest_timestamp_utc, success_timestamp_utc)
    assert succes, error

    assert succes, error
    assert len(html_content) == 2317

    ################### UPDATE 2

    # get the latest log timestamp value
    succes, error, latest_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert succes, error
    assert latest_timestamp_utc is not None
    
    # 2 updates and 1 new 
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST2_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    succes, error, lab_dict, sub_dict, sub_new_list, sub_update_list, success_timestamp = update_edu_data(ENGINE, eduhub_df)

    assert succes, error
    assert len(sub_new_list) == 1
    assert len(sub_update_list) == 2

    succes, error, html_content = summary(lab_dict, sub_dict, sub_new_list, sub_update_list,
        latest_timestamp_utc, success_timestamp_utc)

    assert succes, error
    assert len(html_content) == 3430

    # checking if the log message was created for the update
    session = session_open(ENGINE)
    query_cnt = session.query(func.count(LogsClass.id)).scalar()
    session_close(session)
    assert query_cnt == 2

    ################### UPDATE 3
    
    # get the latest log timestamp value
    succes, error, latest_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert succes, error
    assert latest_timestamp_utc is not None

    # reading in the test data
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST3_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    # putting the data into the database
    succes, error, lab_dict, sub_dict, sub_new_list, sub_update_list, success_timestamp = update_edu_data(ENGINE, eduhub_df)

    assert succes, error
    assert len(sub_new_list) == 0
    assert len(sub_update_list) == 1

    succes, error, html_content = summary(lab_dict, sub_dict, sub_new_list, sub_update_list,
        latest_timestamp_utc, success_timestamp_utc)

    assert succes, error
    assert len(html_content) == 1314
