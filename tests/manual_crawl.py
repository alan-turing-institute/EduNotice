import logging
from sqlalchemy import create_engine

from educrawler.crawler import crawl
from edunotice.edunotice import update_subscriptions
from edunotice.constants import SQL_CONNECTION_STRING_DB


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


if __name__ == "__main__":

    # Running EduCrawler
    args = Namespace(
        course_name="AI for Science & Government (ASG)",
        handout_action="list",
        handout_name=None,
        lab_name=None,
        output="df",
    )

    num_attempts = 5

    for i in range(num_attempts):
        logging.info("EduCrawler attempt: %d / %d " % (i + 1, num_attempts))

        status, error, crawl_df = crawl(args)

        if status:
            break

    if status:
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
    else:
        logging.error("Failed to crawl EduHub")
        logging.error(error)
