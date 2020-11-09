"""
Notifications management module.

"""

import pandas as pd

from sqlalchemy import create_engine

from edunotice.constants import (
    SQL_CONNECTION_STRING_DB,
    CONST_EMAIL_SUBJECT_NEW,
)
from edunotice.notifications import (
    summary, 
    indiv_email_new,
)
from edunotice.sender import send_summary_email, send_email
from edunotice.ingress import update_edu_data, get_latest_log_timestamp
from edunotice import db
from edunotice.utilities import log

ENGINE = create_engine(SQL_CONNECTION_STRING_DB)


def _summary_email(lab_dict, sub_dict, new_sub_list, upd_sub_list,
        latest_timestamp_utc, success_timestamp_utc):
    """
    Prepares and sends out a summary email of new and updated subscriptions.

    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub_list - a list of details of new subscriptions
        upd_sub_list - a list of tuple (before, after) of subscription details
        prev_timestamp_utc - previous crawl timestamp
        curr_timestamp_utc - current crawl timestamp
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    log("Making summary of the registered changes", level=1)
    succes, error, html_content = summary(lab_dict, sub_dict, new_sub_list, upd_sub_list,
        prev_timestamp_utc, curr_timestamp_utc)

    if succes:
        log("Sending summary email", level=1)
        succes, error = send_summary_email(html_content, curr_timestamp_utc)

    return succes, error


def _indv_emails(lab_dict, sub_dict, new_sub_list):
    """
    Prepares and sends out individual emails for new and updated subscriptions.

    Arguments:
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub_list - a list of details of new subscriptions
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    success = True
    error = None

    for new_sub in new_sub_list:

        # generating html content
        html_content = indiv_email_new(lab_dict, sub_dict, new_sub)

        # sending email
        # recipients = new_sub.subscription_users
        log("Sending new subscription email to", level=1)
        # succes, error = send_email(to, CONST_EMAIL_SUBJECT_NEW, html_content)


    return success, error


def notice(args):
    """
    The main routine.

    Arguments:
        args: command line arguments

    Returns:
        success - flag if the action was succesful
        error - error message
    """

    log("Notification service started", level=1)

    if hasattr(args, "input_df"):
        crawl_df = args.input_df

    elif hasattr(args, "input_file"):
        # read the crawl data in
        crawl_df = pd.read_csv(args.input_file)
        log("Read %d data entries" % (len(crawl_df)), level=1)
    else:
        succes = False
        error = "Input data is not provided"

    if succes:
        log("Looking for the latest log timestamp value", level=1)
        succes, error, prev_timestamp_utc = get_latest_log_timestamp(ENGINE)

    if succes:
        if latest_timestamp_utc is None:
            log("No previous logs were found", level=1, indent=2)
        else:
            log("Previous update was made on %s UTC" % (latest_timestamp_utc.strftime("%Y-%m-%d %H:%M")), level=1, indent=2)

        log("Appending DB with the new crawl data", level=1)
        succes, error, lab_dict, sub_dict, new_sub_list, upd_sub_list, curr_timestamp_utc = update_edu_data(ENGINE, crawl_df)
    
    # prep and send summary email
    if success:
         succes, error = _summary_email(lab_dict, sub_dict, new_sub_list, upd_sub_list,
            prev_timestamp_utc, curr_timestamp_utc)

    # prep and send invidual emails
    if success:
        succes, error = _indv_emails(lab_dict, sub_dict, new_sub_list)
    
    return succes, error
