import logging

from educrawler.crawler import crawl


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
        crawl_df['Crawl time utc'] = \
            crawl_df['Crawl time utc'].dt.strftime("%Y-%m-%d %H:%M:%S")

        crawl_df.to_json("ec_output.json", orient="records")

    else:
        logging.error("Failed to crawl EduHub")
        logging.error(error)
