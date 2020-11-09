import datetime
import logging

import azure.functions as func

from educrawler.crawler import crawl
from edunotice.edunotice import notice

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def main(mytimer: func.TimerRequest) -> None:

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    logging.info("EduNotice timer trigger function started at %s", utc_timestamp)

    # Running EduCrawler
    args = Namespace(
        course_name="Research Engineering", 
        handout_action='list', 
        handout_name=None, 
        lab_name=None, 
        output='df')
    
    num_attempts = 3
    attempts = 0

    for i in range(num_attempts):
        logging.info("EduCrawler attempt: %d / %d " % (i+1, num_attempts))

        status, error, crawl_df = crawl(args)

        if status:
            break
    
    if status:
        args = Namespace(input_df=crawl_df)
        status, error = notice(args)
    else:
        logging.error("Failed to crawl EduHub")
        logging.error(error)

    if not status:
        logging.error("Failed to send notification emails")
        logging.error(error)

    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    logging.info("EduNotice timer trigger function finished at %s", utc_timestamp)
