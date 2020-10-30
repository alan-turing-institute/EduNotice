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
        course_name=None, 
        handout_action='list', 
        handout_name=None, 
        lab_name=None, 
        output='csv')
    
    crawl(args)

    args = Namespace(input='ec_output.csv')

    notice(args)

    utc_timestamp = (
        datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    )

    logging.info("EduNotice timer trigger function finished at %s", utc_timestamp)
