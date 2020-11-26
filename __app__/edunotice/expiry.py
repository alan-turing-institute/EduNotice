"""
Time-based notifications module
"""

from datetime import datetime, timezone

from edunotice.notifications import indiv_email_expiry_notification
from edunotice.sender import send_email
from edunotice.utilities import log
from edunotice.db import session_open, session_close
from edunotice.structure import SubscriptionClass, DetailsClass

from edunotice.constants import (
    CONST_EXPR_CODE_0,
    CONST_EXPR_CODE_1,
    CONST_EXPR_CODE_7,
    CONST_EXPR_CODE_30,
    CONST_EMAIL_SUBJECT_EXPIRE,
    CONST_SUB_CANCELLED,
)


def _check_remaining_time(expiry_date, current_date=datetime.utcnow().date()):
    """
    Checks the remaining time by comparing expiry and current dates.

    Arguments:
        expiry_date - expiry date of a subscription
        current_date - current date (default: now)

    Returns:
        expires - flag whether subscription should be notified about the
            amount of time remaining
        expiry_code - expiration code
        days_diff - remaining number of days
    """

    expires = False
    expiry_code = None

    if isinstance(expiry_date, datetime):
        days_diff = (expiry_date.date() - current_date).days
    else:
        days_diff = (expiry_date - current_date).days

    if days_diff < 1:
        expires = True
        expiry_code = CONST_EXPR_CODE_0
    elif days_diff == 1:
        expires = True
        expiry_code = CONST_EXPR_CODE_1
    elif days_diff <= 7:
        expires = True
        expiry_code = CONST_EXPR_CODE_7
    elif days_diff <= 30:
        expires = True
        expiry_code = CONST_EXPR_CODE_30

    return expires, expiry_code, days_diff


def _notify_expiring_sub(session, lab_dict, sub_dict, details, expiry_code, remain_days,
    timestamp_utc=None):
    """
    Sends a time-based notification for an expiring subscription.

    Arguments:
        session - an active sql session
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        details - subscription details
        expiry_code - expiration code
        remain_days - remaining number of days
        timestamp_utc - timestamp when emails were sent (for testing purposes)
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    success, error, html_content = indiv_email_expiry_notification(
        lab_dict, sub_dict, details, remain_days
    )

    if success:
        log(
            "Sending subscription expiry notification email to: %s "
            % (details.subscription_users),
            level=1,
        )

        subject = "%s %d day(s)" % (CONST_EMAIL_SUBJECT_EXPIRE, remain_days)
        success, error = send_email(details.subscription_users, subject, html_content)

        if success:

            if timestamp_utc is not None:
                notice_sent_timestamp = timestamp_utc
            else:
                notice_sent_timestamp = datetime.now(timezone.utc)

            session.query(DetailsClass).filter(DetailsClass.id == details.id).update(
                {
                    "expiry_code": expiry_code,
                    "expiry_notice_sent": notice_sent_timestamp,
                }
            )

            session.query(SubscriptionClass).filter(
                SubscriptionClass.id == details.sub_id
            ).update(
                {
                    "expiry_code": expiry_code,
                    "expiry_notice_sent": notice_sent_timestamp,
                }
            )

            session.commit()

    return success, error


def notify_expire(engine, lab_dict, sub_dict, upd_sub_list, timestamp_utc=None):
    """
    Checks remaining time for updated subscriptions and sends out time-based
        notifications.

        Notification 1: 1 day before end
        Notification 2: 7 days before end
        Notification 3: 30 days before end

    Arguments:
        engine - an sql engine instance
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        upd_sub_list - a list of tuple (before, after) of subscription details
        timestamp_utc - timestamp when emails were sent (for testing purposes)
    Returns:
        success - flag if the action was succesful
        error - error message
        count - the number of nutifications sent
    """

    success = True
    error = None
    count = 0

    if timestamp_utc is None:
        current_date = datetime.utcnow().date()
    else:
        current_date = timestamp_utc.date()

    session = session_open(engine)

    # Notifying updated subscriptions about expiry
    for _, sub_update in enumerate(upd_sub_list):

        send_notification = False

        #prev_details = sub_update[0]
        new_details = sub_update[1]

        # only for active subscriptions. If subscription is cancelled, it should have been notified
        if new_details.subscription_status.lower() == CONST_SUB_CANCELLED.lower():
            continue

        # check the expiration notification code
        expires, expiry_code, remain_days = _check_remaining_time(
            new_details.subscription_expiry_date, current_date=current_date
        )

        if not expires:
            continue

        # check the latest notification code
        sub_latest_noti_code = (
            session.query(SubscriptionClass)
            .filter(SubscriptionClass.id == new_details.sub_id)
            .first()
            .expiry_code
        )

        if sub_latest_noti_code is None:
            send_notification = True
        elif sub_latest_noti_code > expiry_code:
            send_notification = True

        if send_notification:
            send_success, _ = _notify_expiring_sub(session,
                lab_dict, sub_dict, new_details, expiry_code, remain_days,
                timestamp_utc=timestamp_utc)

            if send_success:
                count += 1

    session_close(session)

    return success, error, count
