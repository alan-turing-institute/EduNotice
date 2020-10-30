"""
Notifications management module.

"""

import pandas as pd

from sqlalchemy import create_engine

from edunotice.ingress import (
    update_edu_data,
    get_latest_log_timestamp,
)
from edunotice.notifications import summary
from edunotice.sender import send_summary_email
from edunotice.constants import SQL_CONNECTION_STRING_DB
from edunotice import db
from edunotice.utilities import log

ENGINE = create_engine(SQL_CONNECTION_STRING_DB)

def notice(args):
    """
    The main routine.

    Arguments:
        args: command line arguments
    """

    log("Notification service started", level=1)

    # read the crawl data in
    crawl_df = pd.read_csv(args.input)
    log("Read %d data entries" % (len(crawl_df)), level=1)

    log("Looking for the latest log timestamp value", level=1)
    succes, error, latest_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert succes, error

    if latest_timestamp_utc is None:
        log("No previous logs were found", level=1, indent=2)
    else:
        log("Previous update was made on %s UTC" % (latest_timestamp_utc.strftime("%Y-%m-%d %H:%M")), level=1, indent=2)

    log("Appending DB with the new crawl data", level=1)
    succes, error, lab_dict, sub_dict, sub_new_list, sub_update_list, success_timestamp_utc = update_edu_data(ENGINE, crawl_df)
    assert succes, error

    log("Making summary of the registered changes", level=1)
    succes, error, html_content = summary(lab_dict, sub_dict, sub_new_list, sub_update_list,
        latest_timestamp_utc, success_timestamp_utc)
    assert succes, error

    log("Sending summary email", level=1)
    succes, error = send_summary_email(html_content, success_timestamp_utc)
    assert succes, error