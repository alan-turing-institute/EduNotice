"""
Test edunotice.py module
"""

import os
from datetime import datetime, timezone
import pandas as pd

from sqlalchemy import create_engine

from edunotice.constants import (
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
    CONST_TEST2_FILENAME,
    CONST_TEST3_FILENAME,
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME3,
)

from edunotice.ingress import update_edu_data

from edunotice.edunotice import (
    _notify_subscriptions,
)


ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME3))


def test_notify_subscriptions_1():
    """
    1 new subscription
    """

    indv_email_sent_timestamp_utc = datetime(2020, 10, 20, 10, 20, tzinfo=timezone.utc)

    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    # importing data
    success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list = update_edu_data(
        ENGINE, eduhub_df
    )

    assert success, error
    assert len(new_sub_list) == 2
    assert len(upd_sub_list) == 0

    # sending notices
    success, error, counts = _notify_subscriptions(
        ENGINE,
        lab_dict,
        sub_dict,
        new_sub_list,
        upd_sub_list,
        timestamp_utc=indv_email_sent_timestamp_utc,
    )

    assert success, error
    assert counts[0] == len(new_sub_list)
    assert counts[1] == len(upd_sub_list)
    assert counts[2] == 0
    assert counts[3] == 0


def test_notify_subscriptions_2():
    """
    1 new and 2 updates

    """

    indv_email_sent_timestamp_utc = datetime(2020, 10, 21, 11, 20, tzinfo=timezone.utc)

    # importing data 1 new subscription, 2 updates
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST2_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list = update_edu_data(
        ENGINE, eduhub_df
    )

    assert success, error
    assert len(new_sub_list) == 1
    assert len(upd_sub_list) == 2

    # sending notices
    success, error, counts = _notify_subscriptions(
        ENGINE,
        lab_dict,
        sub_dict,
        new_sub_list,
        upd_sub_list,
        timestamp_utc=indv_email_sent_timestamp_utc,
    )
    assert success, error
    assert counts[0] == len(new_sub_list)
    assert counts[1] == len(upd_sub_list)
    assert counts[2] == 0
    assert counts[3] == 0


def test_notify_subscriptions_3():
    """
    1 usage and 1 expiry

    """

    indv_email_sent_timestamp_utc = datetime(2020, 10, 22, 10, 10, tzinfo=timezone.utc)

    # 1 update - only usage
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST3_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list = update_edu_data(
        ENGINE, eduhub_df
    )

    assert success, error
    assert len(new_sub_list) == 0
    assert len(upd_sub_list) == 3

    # sending notices
    success, error, counts = _notify_subscriptions(
        ENGINE,
        lab_dict,
        sub_dict,
        new_sub_list,
        upd_sub_list,
        timestamp_utc=indv_email_sent_timestamp_utc,
    )
    assert success, error
    assert counts[0] == 0
    assert counts[1] == 0
    assert counts[2] == 1
    assert counts[3] == 1
