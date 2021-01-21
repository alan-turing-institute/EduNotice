"""
Summary notifications module.

"""

from datetime import datetime, timezone

from sqlalchemy import desc, or_

from edunotice.notifications import summary
from edunotice.sender import send_summary_email
from edunotice.ingress import get_latest_log_timestamp, new_log
from edunotice.utilities import log
from edunotice.db import session_open, session_close
from edunotice.structure import DetailsClass
from edunotice.data import get_labs_dict, get_subs_dict


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
        .order_by(
            DetailsClass.subscription_name.asc(),
            DetailsClass.timestamp_utc.asc(),
        )
        .all()
    )

    if len(new_subs) > 0:
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
        .order_by(
            DetailsClass.subscription_name.asc(),
            DetailsClass.timestamp_utc.asc(),
        )
        .all()
    )

    if len(upd_subs) > 0:
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


def _find_sent_notifications(engine, prev_timestamp_utc):
    """
    Looks for updated subscriptions to be included in the summary since
        the last summary.

    Arguments:
        engine - an sql engine instance
        prev_timestamp_utc - timestamp of the previous summary
    Returns:
        success - flag if the action was succesful
        error - error message
        noti_list - a list of details when notifications were sent
    """

    if prev_timestamp_utc is not None:
        wh_clause = or_(
            DetailsClass.new_notice_sent >= prev_timestamp_utc,
            DetailsClass.update_notice_sent >= prev_timestamp_utc,
            DetailsClass.expiry_notice_sent >= prev_timestamp_utc,
            DetailsClass.usage_notice_sent >= prev_timestamp_utc,
        )
    else:
        wh_clause = or_(
            DetailsClass.new_notice_sent.isnot(None),
            DetailsClass.update_notice_sent.isnot(None),
            DetailsClass.expiry_notice_sent.isnot(None),
            DetailsClass.usage_notice_sent.isnot(None),
        )

    session = session_open(engine)

    noti_list = (
        session.query(DetailsClass)
        .filter(wh_clause)
        .order_by(
            DetailsClass.subscription_name.asc(),
            DetailsClass.timestamp_utc.asc(),
        )
        .all()
    )

    if len(noti_list) > 0:
        session.expunge_all()

    return True, None, noti_list


def _prep_summary_email(engine, timestamp_utc=None):
    """
    Prepares and sends out a summary email of new and updated
        subscriptions and notifications sent.

    Arguments:
        engine - an sql engine instance
        timestamp_utc - summary timestamp
    Returns:
        success - flag if the action was succesful
        error - error message
        html_content - html content of the summary email
    """

    if timestamp_utc is None:
        timestamp_utc = datetime.now(timezone.utc)

    html_content = None

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
        log("Looking for new subscriptions", level=1)
        success, error, new_sub_list = _find_new_subs(
            engine, prev_timestamp_utc
        )

    if success:
        log("Looking for updated subscriptions", level=1)
        success, error, upd_sub_list = _find_upd_subs(
            engine, prev_timestamp_utc
        )

    if success:
        log("Looking for sent notifications", level=1)
        success, error, sent_noti_list = _find_sent_notifications(
            engine, prev_timestamp_utc
        )

    if success:
        # find all labs
        success, error, lab_dict = get_labs_dict(engine)

    if success:
        # find all subs
        success, error, sub_dict = get_subs_dict(engine)

    if success:
        # prepare html
        log("Making a summary / html of the registered changes", level=1)

        success, error, html_content = summary(
            lab_dict,
            sub_dict,
            new_sub_list,
            upd_sub_list,
            sent_noti_list,
            prev_timestamp_utc,
            timestamp_utc,
        )

    return success, error, html_content


def summary_email(engine, timestamp_utc=None):
    """
    Prepares and sends out the summary email

    Arguments:
        engine - an sql engine instance
        timestamp_utc - summary timestamp
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    if timestamp_utc is None:
        timestamp_utc = datetime.now(timezone.utc)

    log("Preparing summary email", level=1)

    success, error, html_content = _prep_summary_email(engine, timestamp_utc)

    if success:
        log("Sending summary email", level=1)
        success, error = send_summary_email(html_content, timestamp_utc)

    if success:
        success, error = new_log(engine, timestamp_utc)

    return success, error
