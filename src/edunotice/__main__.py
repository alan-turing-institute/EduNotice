"""
EduHub Notification Service

Tomas Lazauskas
"""

import argparse
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

db.drop_db()
db.create_db()


ENGINE = create_engine(SQL_CONNECTION_STRING_DB)


def set_command_line_args():
    """
    Sets up command line arguments.

    Returns:
        args: command line arguments
    """

    # Command line arguments
    parser = argparse.ArgumentParser(
        description="EduHub Notification Service."
    )

    parser.add_argument(
        "input",
        help="Full path to the EduCrawler output csv file.",
    )

   
    args, _ = parser.parse_known_args()

    return args


def main():
    """
    The main routine.

    """

    # set up command line arguments
    args = set_command_line_args()

    # read the crawl data in
    crawl_df = pd.read_csv(args.input)

    # get the latest log timestamp value
    succes, error, latest_timestamp_utc = get_latest_log_timestamp(ENGINE)
    assert succes, error

    # insert new eduhub crawl data
    succes, error, lab_dict, sub_dict, sub_new_list, sub_update_list, success_timestamp_utc = update_edu_data(ENGINE, crawl_df)
    assert succes, error

    # make summary of the changes
    succes, error, html_content = summary(lab_dict, sub_dict, sub_new_list, sub_update_list,
        latest_timestamp_utc, success_timestamp_utc)
    assert succes, error

    # send summary email
    succes, error = send_summary_email(html_content, success_timestamp_utc)
    assert succes, error


if __name__ == "__main__":

    main()
