import logging
import pandas as pd
from sqlalchemy import create_engine

from edunotice.edunotice import update_subscriptions
from edunotice.constants import SQL_CONNECTION_STRING_DB


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


if __name__ == "__main__":

    crawl_df = pd.read_json("ec_output.json", orient='records')

    args = Namespace(input_df=crawl_df)

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    status, error, counts = update_subscriptions(engine, args)

    logging.info(
        "EduNotice: sent %d new subscription notification" % (counts[0])
    )
    logging.info(
        "EduNotice: sent %d subscription update notification" % (counts[1])
    )
    logging.info(
        "EduNotice: sent %d time-based notification" % (counts[2])
    )
    logging.info(
        "EduNotice: sent %d usage-based notification" % (counts[3])
    )
