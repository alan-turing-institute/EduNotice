"""
Summary notifications module.

"""

from datetime import datetime, timezone
from sqlalchemy import desc
#import pandas as pd

#from sqlalchemy import create_engine, and_

# from edunotice.constants import (
#     SQL_CONNECTION_STRING_DB,
#     CONST_EMAIL_SUBJECT_NEW,
#     CONST_EMAIL_SUBJECT_UPD,
#     CONST_SUB_CANCELLED,
# )
# from edunotice.notifications import (
#     summary,
#     indiv_email_new,
#     indiv_email_upd,
#     details_changed,
# )
#from edunotice.sender import send_summary_email, send_email
from edunotice.ingress import get_latest_log_timestamp, new_log
from edunotice.utilities import log
from edunotice.db import session_open, session_close
from edunotice.structure import DetailsClass


def _find_new_subs(engine, prev_timestamp_utc):
    """
    Looks for new subscriptions to be included in the summary since
        the last summary.

    Arguments:
        engine - an sql engine instance
        prev_timestamp_utc - timestamp of the previous summary
    Returns:
        success - flag if the action was succesful
        error - error message
        new_subs - a lits of new subscriptions to be included in the summary
    """

    if prev_timestamp_utc is not None:
        timestamp_wh = DetailsClass.timestamp_utc >= prev_timestamp_utc
    else:
        timestamp_wh = True

    session = session_open(engine)

    new_subs = (
        session.query(DetailsClass)
        .filter(
            DetailsClass.new_flag,
            timestamp_wh,
        )
        .all()
    )

    session.expunge_all()

    session_close(session)

    return True, None, new_subs


def _find_upd_subs(engine, prev_timestamp_utc):
    """
    Looks for updated subscriptions to be included in the summary since
        the last summary.

    Arguments:
        engine - an sql engine instance
        prev_timestamp_utc - timestamp of the previous summary
    Returns:
        success - flag if the action was succesful
        error - error message
        update_list - a list of tuples (before, after) of subscription details
    """

    update_list = []

    if prev_timestamp_utc is not None:
        timestamp_wh = DetailsClass.timestamp_utc >= prev_timestamp_utc
    else:
        timestamp_wh = True

    session = session_open(engine)

    upd_subs = (
        session.query(DetailsClass)
        .filter(
            DetailsClass.update_flag,
            timestamp_wh,
        )
        .all()
    )

    session.expunge_all()

    # for every updated subscription find its details before the update
    for latest_details in upd_subs:

        # get the latest details before
        prev_details = (
            session.query(DetailsClass)
            .filter(
                DetailsClass.sub_id == latest_details.sub_id,
                DetailsClass.timestamp_utc < latest_details.timestamp_utc,
            )
            .order_by(desc(DetailsClass.timestamp_utc))
            .first()
        )

        session.expunge(prev_details)

        update_list.append((prev_details, latest_details))

    session_close(session)

    return True, None, update_list


def _summary_email_ext(engine, timestamp_utc=datetime.now(timezone.utc)):
    """
    Prepares and sends out a summary email of new and updated subscriptions and notifications sent.

    Arguments:
        engine - an sql engine instance
            lab_dict - lab name /internal id dictionary
            sub_dict - subscription id /internal id dictionary
            new_sub_list - a list of details of new subscriptions
            upd_sub_list - a list of tuple (before, after) of subscription details
        timestamp_utc - summary timestamp
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    # timestamp_utc = datetime.now(timezone.utc)

    log("Looking for the latest log timestamp value", level=1)
    success, error, prev_timestamp_utc = get_latest_log_timestamp(engine)

    if success:
        if prev_timestamp_utc is None:
            log("No previous logs were found", level=1, indent=2)
        else:
            log(
                "Previous update was made on %s UTC"
                % (prev_timestamp_utc.strftime("%Y-%m-%d %H:%M")),
                level=1,
                indent=2,
            )

    if success:
        # collect new subscriptions
        _, _, new_subs = _find_new_subs(engine, prev_timestamp_utc)

        # collect updated subscritions
        _, _, upd_subs = _find_upd_subs(engine, prev_timestamp_utc)

        # # collect sent notifications

    if success:
        # log the successful update
        success, error = new_log(engine, timestamp_utc)

    return success, error


# def _summary_email(
#     lab_dict,
#     sub_dict,
#     new_sub_list,
#     upd_sub_list,
#     prev_timestamp_utc,
#     curr_timestamp_utc,
# ):
#     """
#     Prepares and sends out a summary email of new and updated subscriptions.

#     Arguments:
#         lab_dict - lab name /internal id dictionary
#         sub_dict - subscription id /internal id dictionary
#         new_sub_list - a list of details of new subscriptions
#         upd_sub_list - a list of tuple (before, after) of subscription details
#         prev_timestamp_utc - previous crawl timestamp
#         curr_timestamp_utc - current crawl timestamp
#     Returns:
#         success - flag if the action was succesful
#         error - error message
#     """

#     log("Making summary of the registered changes", level=1)
#     success, error, html_content = summary(
#         lab_dict,
#         sub_dict,
#         new_sub_list,
#         upd_sub_list,
#         prev_timestamp_utc,
#         curr_timestamp_utc,
#     )

#     if success:
#         log("Sending summary email", level=1)
#         success, error = send_summary_email(html_content, curr_timestamp_utc)

#     return success, error
