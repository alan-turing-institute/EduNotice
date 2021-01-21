"""
Notifications management module.

"""

from datetime import datetime, timezone
import pandas as pd

from edunotice.constants import (
    CONST_EMAIL_SUBJECT_NEW,
    CONST_EMAIL_SUBJECT_UPD,
    # CONST_SUB_CANCELLED,
)

from edunotice.notifications import (
    indiv_email_new,
    indiv_email_upd,
    details_changed,
)

from edunotice.sender import send_email
from edunotice.ingress import update_edu_data
from edunotice.utilities import log
from edunotice.db import session_open, session_close
from edunotice.structure import DetailsClass

from edunotice.budget import notify_usage
from edunotice.expiry import notify_expire


def _indv_emails(
    engine, lab_dict, sub_dict, new_sub_list, upd_sub_list, timestamp_utc=None
):
    """
    Prepares and sends out individual emails for new and updated subscriptions.

    Arguments:
        engine - an sql engine instance
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub_list - a list of details of new subscriptions
        upd_sub_list - a list of tuple (before, after) of subscription details
        timestamp_utc - timestamp when emails were sent (for testing purposes)
    Returns:
        success - flag if the action was succesful
        error - error message
        new_count - the number of new subscription nutifications sent
        upd_count - the number of subscription update nutifications sent
    """

    new_count = 0
    upd_count = 0

    session = session_open(engine)

    # Notifying about new subscriptions
    for new_sub in new_sub_list:

        # generating html content
        success, _, html_content = indiv_email_new(lab_dict, sub_dict, new_sub)

        if success:
            # sending email
            log(
                "Sending new subscription email to: %s "
                % (new_sub.subscription_users),
                level=1,
            )
            success, _ = send_email(
                new_sub.subscription_users,
                CONST_EMAIL_SUBJECT_NEW,
                html_content,
            )

            # let's note that the email was sent successfully
            if success:

                if timestamp_utc is not None:
                    notice_sent_timestamp = timestamp_utc
                else:
                    notice_sent_timestamp = datetime.now(timezone.utc)

                session.query(DetailsClass).filter(
                    DetailsClass.id == new_sub.id
                ).update({"new_notice_sent": notice_sent_timestamp})

                session.commit()

                new_count += 1

    # Notifying about updates
    for _, sub_update in enumerate(upd_sub_list):

        prev_details = sub_update[0]
        new_details = sub_update[1]

        send_upd_email = False

        # check which subsciptions have chaged details
        if details_changed(prev_details, new_details):
            send_upd_email = True

        # # checks if the unchanged cancelled subscription's consumption
        # #   has been updated, if so, sends a update notifcation email.
        # switching this functionality off as it takes few days (about 2)
        # for usage date to arrive and the service tends
        # to send too many emails.
        # if (
        #     (
        #         new_details.subscription_status.lower()
        #         == CONST_SUB_CANCELLED.lower()
        #     )
        #     and not details_changed(prev_details, new_details)
        #     and (
        #       prev_details.handout_consumed != new_details.handout_consumed
        #     )
        # ):

        #     send_upd_email = True

        if send_upd_email:

            success, _, html_content = indiv_email_upd(
                lab_dict, sub_dict, sub_update
            )

            if success:
                log(
                    "Sending subscription update email to: %s "
                    % (new_details.subscription_users),
                    level=1,
                )
                success, _ = send_email(
                    new_details.subscription_users,
                    CONST_EMAIL_SUBJECT_UPD,
                    html_content,
                )

                # let's note that the email was sent successfully
                if success:

                    if timestamp_utc is not None:
                        notice_sent_timestamp = timestamp_utc
                    else:
                        notice_sent_timestamp = datetime.now(timezone.utc)

                    session.query(DetailsClass).filter(
                        DetailsClass.id == new_details.id
                    ).update({"update_notice_sent": notice_sent_timestamp})

                    session_close(session)

                    upd_count += 1

    session_close(session)

    return True, None, new_count, upd_count


def _notify_subscriptions(
    engine, lab_dict, sub_dict, new_sub_list, upd_sub_list, timestamp_utc=None
):
    """
    Sends individual notifications

    Arguments:
        engine - an sql engine instance
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
        new_sub_list - a list of details of new subscriptions
        upd_sub_list - a list of tuple (before, after) of subscription details
        timestamp_utc - timestamp when emails were sent (for testing purposes)
    Returns:
        success - flag if the action was succesful
        error - error message
        counts - counts of notifications sent
            (new, update, time-based, usage-based)
    """

    success = True
    error = ""

    # new and update notifications
    sub_success, sub_error, new_count, upd_count = _indv_emails(
        engine,
        lab_dict,
        sub_dict,
        new_sub_list,
        upd_sub_list,
        timestamp_utc=timestamp_utc,
    )

    if not sub_success:
        success = False
        error += sub_error
        log("Time notification error: %s" % (sub_error), level=0)

    # time-based notifications
    time_success, time_error, time_count = notify_expire(
        engine, lab_dict, sub_dict, upd_sub_list, timestamp_utc=timestamp_utc
    )

    if not time_success:
        success = False
        error += time_error
        log("Time notification error: %s" % (time_error), level=0)

    # usage-based notifications
    usage_success, usage_error, usage_count = notify_usage(
        engine, lab_dict, sub_dict, upd_sub_list, timestamp_utc=timestamp_utc
    )

    if not usage_success:
        success = False
        error += usage_error
        log("Usage notification error: %s" % (usage_error), level=0)

    counts = (new_count, upd_count, time_count, usage_count)

    return success, error, counts


def update_subscriptions(engine, args, timestamp_utc=None):
    """
    Sends individual notifications

    Arguments:
        engine - an sql engine instance
        args - command line arguments

    Returns:
        success - flag if the action was succesful
        error - error message
        counts - counts of notifications sent
            (new, update, time-based, usage-based)
    """

    success = True
    error = ""

    new_count = -1
    upd_count = -1
    time_count = -1
    usage_count = -1

    counts = (new_count, upd_count, time_count, usage_count)

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
        log("Appending DB with the new crawl data", level=1)
        (
            success,
            error,
            lab_dict,
            sub_dict,
            new_sub_list,
            upd_sub_list,
        ) = update_edu_data(engine, crawl_df)

    if success:
        log("Sending individual notification emails", level=1)
        success, error, counts = _notify_subscriptions(
            engine,
            lab_dict,
            sub_dict,
            new_sub_list,
            upd_sub_list,
            timestamp_utc=timestamp_utc,
        )

    return success, error, counts
