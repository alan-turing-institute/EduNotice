
from datetime import datetime, timezone

from sqlalchemy import create_engine

from edunotice.constants import SQL_CONNECTION_STRING_DB
from edunotice.summary import _prep_summary_email
from edunotice.sender import send_summary_email

if __name__ == "__main__":

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    timestamp_utc = datetime.now(timezone.utc)

    success, error, html_content = _prep_summary_email(engine, timestamp_utc)

    if success:
        print(html_content)

        success, error = send_summary_email(html_content, timestamp_utc)

        print(success, error)
    else:
        print(success, error)
