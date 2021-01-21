"""
Test expiry.py module
"""

import os
import datetime
import pandas as pd

from sqlalchemy import create_engine

from edunotice.expiry import (
    _check_remaining_time,
    notify_expire,
)

from edunotice.notifications import indiv_email_expiry_notification

from edunotice.ingress import update_edu_data

from edunotice.constants import (
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME4,
    CONST_TEST_DIR_DATA,
    CONST_TEST6_FILENAME,
    CONST_TEST7_FILENAME,
    CONST_TEST12_FILENAME,
    CONST_EXPR_CODE_0,
    CONST_EXPR_CODE_1,
    CONST_EXPR_CODE_7,
    CONST_EXPR_CODE_30,
)

ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME4))


def test_check_remaining_time():
    """
    tests expiry._check_remaining_time routine
    """

    current_date = datetime.datetime(2020, 11, 10).date()

    # -1 day
    expires, expiry_code, remain_days = _check_remaining_time(
        datetime.datetime(2020, 11, 9).date(), current_date=current_date
    )

    assert expires
    assert expiry_code == CONST_EXPR_CODE_0
    assert remain_days == -1

    # 0 days
    expires, expiry_code, remain_days = _check_remaining_time(
        datetime.datetime(2020, 11, 10).date(), current_date=current_date
    )

    assert expires
    assert expiry_code == CONST_EXPR_CODE_0

    # 1 day
    expires, expiry_code, remain_days = _check_remaining_time(
        datetime.datetime(2020, 11, 11).date(), current_date=current_date
    )

    assert expires
    assert expiry_code == CONST_EXPR_CODE_1

    # 5 days
    expires, expiry_code, remain_days = _check_remaining_time(
        datetime.datetime(2020, 11, 16).date(), current_date=current_date
    )

    assert expires
    assert expiry_code == CONST_EXPR_CODE_7

    # 7 days
    expires, expiry_code, remain_days = _check_remaining_time(
        datetime.datetime(2020, 11, 17).date(), current_date=current_date
    )

    assert expires
    assert expiry_code == CONST_EXPR_CODE_7
    assert remain_days == 7

    # 14 days
    expires, expiry_code, remain_days = _check_remaining_time(
        datetime.datetime(2020, 11, 24).date(), current_date=current_date
    )

    assert expires
    assert expiry_code == CONST_EXPR_CODE_30
    assert remain_days == 14

    # 30 days
    expires, expiry_code, remain_days = _check_remaining_time(
        datetime.datetime(2020, 12, 10).date(), current_date=current_date
    )

    assert expires
    assert expiry_code == CONST_EXPR_CODE_30
    assert remain_days == 30

    # 70 days (longer than 30 days)
    expires, expiry_code, remain_days = _check_remaining_time(
        datetime.datetime(2021, 1, 19).date(), current_date=current_date
    )

    assert not expires
    assert expiry_code is None
    assert remain_days == 70


def test_expiry():
    """
    The main routine to test the expiry module
    """

    current_date = datetime.datetime(2020, 11, 10)

    # new subscriptions
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST6_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    (
        success,
        error,
        lab_dict,
        sub_dict,
        sub_new_list,
        sub_update_list,
    ) = update_edu_data(ENGINE, eduhub_df)

    assert success, error
    assert len(sub_new_list) == 5
    assert len(sub_update_list) == 0

    # updates
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST7_FILENAME)
    eduhub_df = pd.read_csv(file_path)
    (
        success,
        error,
        lab_dict,
        sub_dict,
        sub_new_list,
        sub_update_list,
    ) = update_edu_data(ENGINE, eduhub_df)

    assert success, error
    assert len(sub_new_list) == 1
    assert len(sub_update_list) == 5

    # expires in the future (more than 30 days)
    sub_details = sub_update_list[0][1]
    expires, expiry_code, remain_days = _check_remaining_time(
        sub_details.subscription_expiry_date, current_date=current_date.date()
    )
    assert not expires

    # expires in less than 30 days
    sub_details = sub_update_list[1][1]
    _, _, remain_days = _check_remaining_time(
        sub_details.subscription_expiry_date, current_date=current_date.date()
    )
    success, error, html_content = indiv_email_expiry_notification(
        lab_dict, sub_dict, sub_details, remain_days
    )

    assert len(html_content) == 3282

    # expires in 1 day
    sub_details = sub_update_list[2][1]
    _, _, remain_days = _check_remaining_time(
        sub_details.subscription_expiry_date, current_date=current_date.date()
    )
    success, error, html_content = indiv_email_expiry_notification(
        lab_dict, sub_dict, sub_details, remain_days
    )

    assert len(html_content) == 3280

    # send notifications
    success, error, count = notify_expire(
        ENGINE, lab_dict, sub_dict, sub_update_list, timestamp_utc=current_date
    )
    assert success, error
    assert count == 2


def test_expiry_update():
    """
    Additional routine to test the expiry module.

    In this test we cover the scenatio when expiry date is updated.

    """

    current_date = datetime.datetime(2020, 11, 11)

    # updates
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST12_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    (
        success,
        error,
        lab_dict,
        sub_dict,
        sub_new_list,
        sub_update_list,
    ) = update_edu_data(ENGINE, eduhub_df)

    assert success, error
    assert len(sub_new_list) == 0
    assert len(sub_update_list) == 4

    # send notifications
    success, error, count = notify_expire(
        ENGINE,
        lab_dict,
        sub_dict,
        sub_update_list,
        timestamp_utc=current_date,
    )
    assert success, error
    assert count == 3
