"""
Test edunotice.py module
"""

import os
import pytest
import pandas as pd

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

from edunotice.edunotice import _summary_email, _indv_emails

TEST_EMAIL_API = pytest.mark.skipif(not SG_TEST_EMAIL, reason="Testing Email API is switched off")

ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME3))


@TEST_EMAIL_API
def test_summary_email():

    succes, error, prev_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert succes, error

    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    succes, error, lab_dict, sub_dict, new_sub_list, upd_sub_list, curr_timestamp_utc = update_edu_data(ENGINE, eduhub_df)

    assert succes, error
    assert len(new_sub_list) == 2
    assert len(upd_sub_list) == 0

    succes, error = _summary_email(lab_dict, sub_dict, new_sub_list, upd_sub_list,
            prev_timestamp_utc, curr_timestamp_utc)
    assert succes, error

    # 1 new subscription, 2 updates
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST2_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    succes, error, lab_dict, sub_dict, new_sub_list, upd_sub_list, curr_timestamp_utc = update_edu_data(ENGINE, eduhub_df)

    assert succes, error
    assert len(new_sub_list) == 1
    assert len(upd_sub_list) == 2

    succes, error = _indv_emails(ENGINE, lab_dict, sub_dict, new_sub_list, upd_sub_list)
    assert succes, error

    # 1 update - only usage
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST3_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    succes, error, lab_dict, sub_dict, new_sub_list, upd_sub_list, curr_timestamp_utc = update_edu_data(ENGINE, eduhub_df)

    assert succes, error
    assert len(new_sub_list) == 0
    assert len(upd_sub_list) == 1

    succes, error = _indv_emails(ENGINE, lab_dict, sub_dict, new_sub_list, upd_sub_list)
    assert succes, error
