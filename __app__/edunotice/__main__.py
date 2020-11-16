"""
EduHub Activity Notification Service

Tomas Lazauskas
"""

import argparse
from sqlalchemy import create_engine

from edunotice.edunotice import notice
from edunotice.constants import SQL_CONNECTION_STRING_DB

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


def main(args):
    """
    The main routine.

    Arguments:
        args: command line arguments
    """

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    notice(engine, args)


if __name__ == "__main__":

    # set up command line arguments
    args = set_command_line_args()
    
    # run the service
    main(args)
