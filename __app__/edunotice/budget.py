"""
Usage-based notifications module
"""

from datetime import datetime, timezone

from edunotice.notifications import indiv_email_usage_notification#, details_changed
from edunotice.sender import send_email
from edunotice.utilities import log
from edunotice.db import session_open, session_close
from edunotice.structure import SubscriptionClass, DetailsClass

from edunotice.constants import (
    CONST_SUB_CANCELLED,
    CONST_USAGE_CODE_50,
    CONST_USAGE_CODE_75,
    CONST_USAGE_CODE_90,
    CONST_USAGE_CODE_95,
    CONST_EMAIL_SUBJECT_USAGE,
)


def usage_notification(budget, usage):
    """
    Estimates utilisation percentage and checks whether subscription should
        be notified about it.

    Arguments:
        budget - subscription's budget
        usage - subscription's usage

    Returns:
        notify - flag whether subscription should be notified about its usage
        notification_code - notification code
    """

    notify = False
    notification_code = None

    if budget == None or budget == 0:
        utilisation = 0.0
    else:
        utilisation = float(usage) / float(budget)
    
    if utilisation >= 0.5:
        notify = True

        if utilisation >= 0.95:
            notification_code = CONST_USAGE_CODE_95
        elif utilisation >= 0.90:
            notification_code = CONST_USAGE_CODE_90
        elif utilisation >= 0.75:
            notification_code = CONST_USAGE_CODE_75
        else:
            notification_code = CONST_USAGE_CODE_50
    
    return notify, notification_code


def notify_usage_sub(session, lab_dict, sub_dict, details, usage_code):
    """
    Sends a usage-based notification.

    Arguments:
        session - an active sql session
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        details - subscription details
        usage_code - usage code
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    success, error, html_content = indiv_email_usage_notification(lab_dict, sub_dict, details, usage_code)

    if success:
        log("Sending subscription utilisation email to: %s -> %s " % (details.subscription_name, details.subscription_users), level=1)

        subject = "%s %d%%" % (CONST_EMAIL_SUBJECT_USAGE, usage_code)

        success, error = send_email(details.subscription_users, subject, html_content)

        if success:
            
            session.query(DetailsClass).\
                filter(DetailsClass.id == details.id).\
                update({
                    "usage_code": usage_code,
                    "usage_notice_sent": datetime.now(timezone.utc),
                })

            session.query(SubscriptionClass).\
                filter(SubscriptionClass.id == details.sub_id).\
                update({
                    "usage_code": usage_code,
                    "usage_notice_sent": datetime.now(timezone.utc),
                })
            
            session.commit()

    return success, error


def notify_usage(engine, lab_dict, sub_dict, upd_sub_list, current_date=datetime.utcnow().date()):
    """
    Checks remaining budgets for new and updated subscriptions and sends out usage-based
        notifications. 

        Notification 1: 50% of monetary credit has been used
        Notification 2: 75% of monetary credit has been used
        Notification 3: 90% of monetary credit has been used
        Notification 4: 95% of monetary credit has been used

    Arguments:
        engine - an sql engine instance
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        upd_sub_list - a list of tuple (before, after) of subscription details
        current_date - current date (default: now)
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    success = True
    error = None

    session = session_open(engine)

    # Notifying updated subscriptions
    for i, sub_update in enumerate(upd_sub_list):
        
        send_notification = False

        prev_details = sub_update[0]
        new_details = sub_update[1]

        # only for active subscriptions. If subscription is cancelled, it should have been alerady notified 
        if (new_details.subscription_status.lower() == CONST_SUB_CANCELLED.lower()):
            continue

        # check the budget notification code
        notify, usage_code = usage_notification(new_details.handout_budget, new_details.handout_consumed)

        if not notify:
            continue

        # check the latest notification code
        sub_latest_noti_code = (
            session.query(SubscriptionClass)
            .filter(SubscriptionClass.id == new_details.sub_id)
            .first()
            .usage_code
        )

        if sub_latest_noti_code == None:
            send_notification = True
        
        if send_notification:
            _, _ = notify_usage_sub(session, lab_dict, sub_dict, new_details, usage_code)
         
    session_close(session)

    return success, error
