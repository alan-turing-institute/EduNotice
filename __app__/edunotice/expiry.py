import datetime

from edunotice.constants import (
    CONST_EXPR_CODE_0,
    CONST_EXPR_CODE_1,
    CONST_EXPR_CODE_7,
    CONST_EXPR_CODE_30,
)

def check_remaining_time(expiry_date, current_date=datetime.datetime.utcnow().date()):
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

    if isinstance(expiry_date, datetime.datetime):
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


def notify_expiring_subs(engine, lab_dict, sub_dict, new_sub_list, upd_sub_list,
    current_date=datetime.datetime.utcnow().date()):
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

    # Notifying updated subscriptions about expiry
    for i, sub_update in enumerate(upd_sub_list):

        prev_details = sub_update[0]
        new_details = sub_update[1]

        # check if expiry date has been updated
        if prev_details.subscription_expiry_date != new_details.subscription_expiry_date:
            
            # check if subscription is about to expire
            expires, expiry_code, remain_days = check_remaining_time(new_details.subscription_expiry_date, current_date=current_date)

            # send a time-based notification if subscriptions expires
            if expires and expiry_code != CONST_EXPR_CODE_0:
                print(expires, expiry_code, remain_days)

    return success, error