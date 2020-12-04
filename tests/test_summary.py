"""
Test summary.py module
"""

import os
import pandas as pd

from datetime import datetime, timezone

from sqlalchemy import create_engine

from edunotice.constants import (
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
    CONST_TEST2_FILENAME,
    CONST_TEST3_FILENAME,
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME7,
)

from edunotice.ingress import update_edu_data, get_latest_log_timestamp
from edunotice.edunotice import _notify_subscriptions

from edunotice.summary import (
    _find_new_subs,
    _find_upd_subs,
    _prep_summary_email,
    _find_sent_notifications,
    summary_email,
)


ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME7))


def test_summary_new():
    """
    Testing summary 1 subscription
    """

    prev_summary_timestamp_utc = None
    indv_email_sent_timestamp_utc = datetime(2020, 10, 20, 10, 20, tzinfo=timezone.utc)
    new_summary_timestamp_utc = datetime(2020, 10, 20, 10, 30, tzinfo=timezone.utc)

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

    # finding new subscriptions for the summary
    success, error, new_subs = _find_new_subs(ENGINE, prev_summary_timestamp_utc)
    assert success, error
    assert len(new_subs) == counts[0]

    # finding updated subscriptions for the summary
    success, error, upd_subs = _find_upd_subs(ENGINE, prev_summary_timestamp_utc)
    assert success, error
    assert len(upd_subs) == counts[1]

    # finding notifications sent for the summary
    success, error, sent_noti = _find_sent_notifications(
        ENGINE, prev_summary_timestamp_utc
    )
    assert success, error
    assert len(sent_noti) == counts[0]

    # preps a summary email
    success, error, html_content = _prep_summary_email(
        ENGINE, timestamp_utc=new_summary_timestamp_utc
    )
    assert success, error
    assert len(html_content) in (2854, 2851)

    # preps and sends out summary email
    success, error = summary_email(ENGINE, timestamp_utc=new_summary_timestamp_utc)
    assert success, error


def test_summary_upd():
    """
    Testing summary 1 new and 2 updates

    """

    success, error, prev_summary_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert success, error

    indv_email_sent_timestamp_utc = datetime(2020, 10, 21, 11, 20, tzinfo=timezone.utc)
    new_summary_timestamp_utc = datetime(2020, 10, 21, 11, 30, tzinfo=timezone.utc)

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

    # finding new subscriptions for the summary
    success, error, new_subs = _find_new_subs(ENGINE, prev_summary_timestamp_utc)
    assert success, error
    assert len(new_subs) == counts[0]

    # finding updated subscriptions for the summary
    success, error, new_subs = _find_upd_subs(ENGINE, prev_summary_timestamp_utc)
    assert success, error
    assert len(new_subs) == counts[1]

    # finding notifications sent for the summary
    success, error, sent_noti = _find_sent_notifications(
        ENGINE, prev_summary_timestamp_utc
    )
    assert success, error
    assert len(sent_noti) == counts[0] + counts[1]

    # preps a summary email
    success, error, html_content = _prep_summary_email(
        ENGINE, timestamp_utc=new_summary_timestamp_utc
    )
    assert success, error
    assert len(html_content) in (4075, 4071)

    # preps and sends out summary email
    success, error = summary_email(ENGINE, timestamp_utc=new_summary_timestamp_utc)
    assert success, error


def test_summary_upd_2():
    """
    Testing summary 1 usage and 1 expiry notification

    """

    success, error, prev_summary_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert success, error

    indv_email_sent_timestamp_utc = datetime(2020, 10, 22, 10, 10, tzinfo=timezone.utc)
    new_summary_timestamp_utc = datetime(2020, 10, 22, 11, 30, tzinfo=timezone.utc)

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

    # finding new subscriptions for the summary
    success, error, new_subs = _find_new_subs(ENGINE, prev_summary_timestamp_utc)
    assert success, error
    assert len(new_subs) == counts[0]

    # finding updated subscriptions for the summary
    success, error, new_subs = _find_upd_subs(ENGINE, prev_summary_timestamp_utc)
    assert success, error
    assert len(new_subs) == counts[1]

    # finding notifications sent for the summary
    success, error, sent_noti = _find_sent_notifications(
        ENGINE, prev_summary_timestamp_utc
    )
    assert success, error
    assert len(sent_noti) == counts[0] + counts[1] + counts[2] + counts[3]

    # preps a summary email
    success, error, html_content = _prep_summary_email(
        ENGINE, timestamp_utc=new_summary_timestamp_utc
    )
    assert success, error
    assert len(html_content) in (1889, 1885)

    # preps and sends out summary email
    success, error = summary_email(ENGINE, timestamp_utc=new_summary_timestamp_utc)
    assert success, error
