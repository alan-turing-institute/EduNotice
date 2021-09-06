"""
Test budget.py module
"""

import os
import pandas as pd

from sqlalchemy import create_engine

from edunotice.ingress import update_edu_data
from edunotice.budget import _usage_notification, notify_usage
from edunotice.notifications import indiv_email_usage_notification

from edunotice.constants import (
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME5,
    CONST_TEST_DIR_DATA,
    CONST_TEST8_FILENAME,
    CONST_TEST9_FILENAME,
    CONST_TEST10_FILENAME,
    CONST_TEST11_FILENAME,
    CONST_USAGE_CODE_50,
    CONST_USAGE_CODE_75,
    CONST_USAGE_CODE_90,
    CONST_USAGE_CODE_95,
)


ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME5))


def test_usage():
    """
    The main routine to test the budget module
    """

    # new subscriptions
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST8_FILENAME)
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
    assert len(sub_new_list) == 6
    assert len(sub_update_list) == 0

    # updates
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST9_FILENAME)
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
    assert len(sub_update_list) == 6

    # usage more than 50%
    sub_details = sub_update_list[2][1]
    notify, usage_code = _usage_notification(
        sub_details.handout_budget, sub_details.handout_consumed
    )
    assert notify
    assert usage_code == CONST_USAGE_CODE_50

    success, error, html_content = indiv_email_usage_notification(
        lab_dict, sub_dict, sub_details, usage_code
    )
    assert success, error
    assert len(html_content) == 3750

    # usage more than 75%
    sub_details = sub_update_list[3][1]
    notify, usage_code = _usage_notification(
        sub_details.handout_budget, sub_details.handout_consumed
    )
    assert notify
    assert usage_code == CONST_USAGE_CODE_75

    success, error, html_content = indiv_email_usage_notification(
        lab_dict, sub_dict, sub_details, usage_code
    )
    assert success, error

    # usage more than 90%
    sub_details = sub_update_list[4][1]
    notify, usage_code = _usage_notification(
        sub_details.handout_budget, sub_details.handout_consumed
    )
    assert notify
    assert usage_code == CONST_USAGE_CODE_90

    success, error, html_content = indiv_email_usage_notification(
        lab_dict, sub_dict, sub_details, usage_code
    )
    assert success, error

    # usage more than 95%
    sub_details = sub_update_list[5][1]
    notify, usage_code = _usage_notification(
        sub_details.handout_budget, sub_details.handout_consumed
    )
    assert notify
    assert usage_code == CONST_USAGE_CODE_95

    success, error, html_content = indiv_email_usage_notification(
        lab_dict, sub_dict, sub_details, usage_code
    )
    assert success, error

    # send notifications
    success, error, count = notify_usage(
        ENGINE, lab_dict, sub_dict, sub_update_list
    )
    assert success, error
    assert count == 4

    # updates
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST10_FILENAME)
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
    assert len(sub_update_list) == 2

    # send notifications
    #   1 changed code from 50 to 90
    #   the other did not change its code
    success, error, count = notify_usage(
        ENGINE, lab_dict, sub_dict, sub_update_list
    )
    assert success, error
    assert count == 1


def test_usage_update():
    """
    Additional routine to test the budget module.

    In this test we cover the scenatio when budget value is updated.

    """

    # updates
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST11_FILENAME)
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
    #   1 changed code from 50 to 90
    #   the other did not change its code
    success, error, count = notify_usage(
        ENGINE, lab_dict, sub_dict, sub_update_list
    )
    assert success, error
    assert count == 2
