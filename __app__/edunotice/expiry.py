"""
Time-based notifications module
"""

from datetime import datetime, timezone

from edunotice.notifications import indiv_email_expiry_notification, details_changed
from edunotice.sender import send_email
from edunotice.utilities import log
from edunotice.db import session_open, session_close
from edunotice.structure import DetailsClass

from edunotice.constants import (
    CONST_EXPR_CODE_0,
    CONST_EXPR_CODE_1,
    CONST_EXPR_CODE_7,
    CONST_EXPR_CODE_30,
    CONST_EMAIL_SUBJECT_EXPIRE,
    CONST_SUB_CANCELLED,
)

def check_remaining_time(expiry_date, current_date=datetime.utcnow().date()):
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


def notify_expiring_sub(session, lab_dict, sub_dict, details, expiry_code, remain_days):
    """
    Sends a time-based notification for an expiring subscription.

    Arguments:
        session - an active sql session
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        details - subscription details
        expiry_code - expiration code
        days_diff - remaining number of days
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    success, error, html_content = indiv_email_expiry_notification(lab_dict, sub_dict, details, expiry_code, remain_days)

    if success:
        log("Sending subscription update email to: %s " % (details.subscription_users), level=1)

        subject = "%s %d day(s)" %(CONST_EMAIL_SUBJECT_EXPIRE, remain_days)
        success, error = send_email(details.subscription_users, CONST_EMAIL_SUBJECT_EXPIRE, html_content)

        if success:
            
            session.query(DetailsClass).\
                filter(DetailsClass.id == details.id).\
                update({
                    "expiry_code": expiry_code,
                    "expiry_notice_sent": datetime.now(timezone.utc),
                })

            session.commit()
    
    return success, error
    

def notify_expiring_subs(engine, lab_dict, sub_dict, new_sub_list, upd_sub_list,
    current_date=datetime.utcnow().date()):
    """
    Checks remaining time for new and updated subscriptions and sends out time-based
        notifications. 

        Notification 1: 1 day before end
        Notification 2: 7 days before end
        Notification 3: 30 days before end

    Arguments:
        engine - an sql engine instance
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub_list - a list of details of new subscriptions
        upd_sub_list - a list of tuple (before, after) of subscription details
        current_date - current date (default: now)
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    success = True
    error = None

    session = session_open(engine)

    # Notifying about new subscriptions
    for new_details in new_sub_list:

        # check if subscription is about to expire
        expires, expiry_code, remain_days = check_remaining_time(new_details.subscription_expiry_date, current_date=current_date)

        if expires and expiry_code != CONST_EXPR_CODE_0:

            _, _ = notify_expiring_sub(session, lab_dict, sub_dict, new_details, expiry_code, remain_days)

    # Notifying updated subscriptions about expiry
    for i, sub_update in enumerate(upd_sub_list):
        
        send_notification = False

        prev_details = sub_update[0]
        new_details = sub_update[1]

        # only for active subscriptions. If subscription is cancelled, it should have been notified 
        if (new_details.subscription_status.lower() == CONST_SUB_CANCELLED.lower()):
            continue

        # check if subscription is about to expire
        expires, expiry_code, remain_days = check_remaining_time(new_details.subscription_expiry_date, current_date=current_date)

        if expires and expiry_code != CONST_EXPR_CODE_0:
            
            # check if expiry date has been updated
            if prev_details.subscription_expiry_date != new_details.subscription_expiry_date:
                send_notification = True
            # check if notification has already been sent
            elif prev_details.expiry_code is None or prev_details.expiry_code != expiry_code:
                send_notification = True

            # send a time-based notification if subscriptions expires
            if send_notification:
                _, _ = notify_expiring_sub(session, lab_dict, sub_dict, new_details, expiry_code, remain_days)
                
    session_close(session)

    return success, error