"""
Notifications management module.

"""

from datetime import datetime, timezone
import pandas as pd

from sqlalchemy import create_engine

from edunotice.constants import (
    SQL_CONNECTION_STRING_DB,
    CONST_EMAIL_SUBJECT_NEW,
    CONST_EMAIL_SUBJECT_UPD,
)
from edunotice.notifications import (
    summary, 
    indiv_email_new,
    indiv_email_upd,
    details_changed
)
from edunotice.sender import send_summary_email, send_email
from edunotice.ingress import update_edu_data, get_latest_log_timestamp
from edunotice.utilities import log
from edunotice.db import session_open, session_close
from edunotice.structure import DetailsClass


def _summary_email(lab_dict, sub_dict, new_sub_list, upd_sub_list,
        prev_timestamp_utc, curr_timestamp_utc):
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


def _indv_emails(engine, lab_dict, sub_dict, new_sub_list, upd_sub_list):
    """
    Prepares and sends out individual emails for new and updated subscriptions.

    Arguments:
        engine - an sql engine instance
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub_list - a list of details of new subscriptions
        upd_sub_list - a list of tuple (before, after) of subscription details
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    # Notifying about new subscriptions
    for new_sub in new_sub_list:

        # generating html content
        success, error, html_content = indiv_email_new(lab_dict, sub_dict, new_sub)
        
        if success:
            # sending email
            log("Sending new subscription email to: %s " % (new_sub.subscription_users), level=1)
            #success, error = send_email(new_sub.subscription_users, CONST_EMAIL_SUBJECT_NEW, html_content)
            
            # let's note that the email was sent successfully
            if success:
                session = session_open(engine)

                session.query(DetailsClass).\
                    filter(DetailsClass.id == new_sub.id).\
                    update({"email_sent": datetime.now(timezone.utc)})

                session.commit()
                session_close(session)

    # Notifying about updates
    for i, sub_update in enumerate(upd_sub_list):
        
        prev_details = sub_update[0]
        new_details = sub_update[1]

        # check which subsciptions have chaged details
        if details_changed(prev_details, new_details):
            
            success, error, html_content = indiv_email_upd(lab_dict, sub_dict, sub_update)

            if success:
                log("Sending subscription update email to: %s " % (new_details.subscription_users), level=1)
                #success, error = send_email(new_details.subscription_users, CONST_EMAIL_SUBJECT_UPD, html_content)

                # let's note that the email was sent successfully
                if success:
                    
                    session = session_open(engine)

                    session.query(DetailsClass).\
                        filter(DetailsClass.id == new_details.id).\
                        update({"email_sent": datetime.now(timezone.utc)})

                    session.commit()
                    session_close(session)

    return True, None


def notice(engine, args):
    """
    The main routine.

    Arguments:
        engine - an sql engine instance
        args: command line arguments

    Returns:
        success - flag if the action was succesful
        error - error message
    """

    success = True
    error = None
    prev_timestamp_utc = None

    log("Notification service started", level=1)

    if hasattr(args, "input_df"):
        crawl_df = args.input_df

    elif hasattr(args, "input_file"):
        # read the crawl data in
        crawl_df = pd.read_csv(args.input_file)
        log("Read %d data entries" % (len(crawl_df)), level=1)
    else:
        success = False
        error = "Input data is not provided"

    if success:
        log("Looking for the latest log timestamp value", level=1)
        success, error, prev_timestamp_utc = get_latest_log_timestamp(engine)

    if success:
        if prev_timestamp_utc is None:
            log("No previous logs were found", level=1, indent=2)
        else:
            log("Previous update was made on %s UTC" % (prev_timestamp_utc.strftime("%Y-%m-%d %H:%M")), level=1, indent=2)

        log("Appending DB with the new crawl data", level=1)
        success, error, lab_dict, sub_dict, new_sub_list, upd_sub_list, curr_timestamp_utc = update_edu_data(engine, crawl_df)
    
    # prep and send summary email
    if success:
         success, error = _summary_email(lab_dict, sub_dict, new_sub_list, upd_sub_list,
            prev_timestamp_utc, curr_timestamp_utc)

    # # prep and send invidual emails
    # if success:
    #     success, error = _indv_emails(engine, lab_dict, sub_dict, new_sub_list)
    
    return success, error
