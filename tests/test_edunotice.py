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

from edunotice.edunotice import _summary_email, _indv_emails, _summary_email_ext

TEST_EMAIL_API = pytest.mark.skipif(not SG_TEST_EMAIL, reason="Testing Email API is switched off")

ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME3))


@TEST_EMAIL_API
def test_summary_email():

    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list = update_edu_data(ENGINE, eduhub_df)

    assert success, error
    assert len(new_sub_list) == 2
    assert len(upd_sub_list) == 0

    success, error = _summary_email_ext(ENGINE)
    assert success, error

    assert False

    # success, error = _summary_email(lab_dict, sub_dict, new_sub_list, upd_sub_list,
    #         prev_timestamp_utc, curr_timestamp_utc)
    # assert success, error

    # # 1 new subscription, 2 updates
    # file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST2_FILENAME)
    # eduhub_df = pd.read_csv(file_path)

    # success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list, curr_timestamp_utc = update_edu_data(ENGINE, eduhub_df)

    # assert success, error
    # assert len(new_sub_list) == 1
    # assert len(upd_sub_list) == 2

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