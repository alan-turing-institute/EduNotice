"""
Test summary.py module
"""

import os
import pytest
import pandas as pd

from datetime import datetime, timezone

from sqlalchemy import create_engine

from edunotice.constants import(
    SG_TEST_EMAIL,
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
    CONST_TEST2_FILENAME,
    CONST_TEST3_FILENAME,
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME3
)

from edunotice.ingress import update_edu_data, get_latest_log_timestamp
from edunotice.edunotice import _indv_emails

from edunotice.summary import _find_new_subs, _find_upd_subs, _summary_email_ext


ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME3))


def test_summary_new():
    """
    Testing summary only with new subscriptions
    """

    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    # importing data
    success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list = update_edu_data(ENGINE, eduhub_df)

    assert success, error
    assert len(new_sub_list) == 2
    assert len(upd_sub_list) == 0

    # sending notices
    success, error, new_count, upd_count = _indv_emails(ENGINE, lab_dict, sub_dict, new_sub_list, upd_sub_list)
    assert success, error
    assert new_count == 2
    assert upd_count == 0

    # finding new subscriptions for the summary
    success, error, new_subs = _find_new_subs(ENGINE, None)
    assert success, error
    assert len(new_subs) == 2

    timestamp_utc=datetime(2020,10,20,10,30,tzinfo=timezone.utc)

    success, error = _summary_email_ext(ENGINE, timestamp_utc=timestamp_utc)
    assert success, error

    
def test_summary_upd():
    """
    Testing summary one new and 2 updates

    """

    success, error, prev_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert success, error

    # importing data 1 new subscription, 2 updates
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST2_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list = update_edu_data(ENGINE, eduhub_df)
    
    assert success, error
    assert len(new_sub_list) == 1
    assert len(upd_sub_list) == 2

    # sending notices
    success, error, new_count, upd_count = _indv_emails(ENGINE, lab_dict, sub_dict, new_sub_list, upd_sub_list)
    assert success, error
    assert new_count == 1
    assert upd_count == 2

    # finding new subscriptions for the summary
    success, error, new_subs = _find_new_subs(ENGINE, prev_timestamp_utc)
    assert success, error
    assert len(new_subs) == 1

    # finding updated subscriptions for the summary
    success, error, new_subs = _find_upd_subs(ENGINE, prev_timestamp_utc)
    assert success, error
    assert len(new_subs) == 2

    timestamp_utc=datetime(2020,10,20,23,30,tzinfo=timezone.utc)

    success, error = _summary_email_ext(ENGINE, timestamp_utc=timestamp_utc)
    assert success, error




    # success, error, new_count, upd_count = _indv_emails(ENGINE, lab_dict, sub_dict, new_sub_list, upd_sub_list)
    # assert success, error
    # assert new_count == 1
    # assert upd_count == 2

    # # 1 update - only usage
    # file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST3_FILENAME)
    # eduhub_df = pd.read_csv(file_path)

    # success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list, curr_timestamp_utc = update_edu_data(ENGINE, eduhub_df)

    # assert success, error
    # assert len(new_sub_list) == 0
    # assert len(upd_sub_list) == 1

    # success, error, new_count, upd_count = _indv_emails(ENGINE, lab_dict, sub_dict, new_sub_list, upd_sub_list)
    # assert success, error
    # assert new_count == 0
    # assert upd_count == 0 # details didn't change

    assert False