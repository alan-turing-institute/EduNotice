import datetime
import logging
import sys
import os.path
import azure.functions as func

from sqlalchemy import create_engine

from edunotice.summary import summary_email
from edunotice.constants import SQL_CONNECTION_STRING_DB

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def main(mytimer: func.TimerRequest) -> None:

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    logging.info("EduNotice summary function started at %s", utc_timestamp)

    success, error = summary_email(engine)

    if success:
        logging.info("EduNotice summary sent")
    else:
        logging.info("EduNotice summary failed: %s" % (error))

    logging.info("EduNotice summary function finished at %s", utc_timestamp)
