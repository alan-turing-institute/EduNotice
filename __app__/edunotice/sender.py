"""
Email sending module
"""

import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail

from edunotice.constants import (
    SG_FROM_EMAIL,
    SG_SUMMARY_RECIPIENTS,
    SG_API_KEY,
    SG_TEST_EMAIL,
    SG_TEST_FROM,
    SG_TEST_TO,
    SG_EMAIL_DISABLE,
    SG_EMAIL_EXCL,
)

SG_CLIENT = sendgrid.SendGridAPIClient(api_key=SG_API_KEY)


def _prep_to_list(to_str):
    """
    Prepares a list of unique recipients

    Arguments:
        to - comma separated list of recipients
    Return:
        to_list - unique list of recipients
    """

    if isinstance(to_str, list):
        to_arr = to_str
    elif to_str is None:
        return []
    else:
        to_arr = [x.strip() for x in to_str.split(",")]

    to_arr = list(set(to_arr))  # making sure that values are unique

    to_list = []
    for to_arr_el in to_arr:
        to_list.append(To(to_arr_el))

    return to_list


def send_email(to_str, subject, html_content):
    """
    A function to send an email

    Arguments:
        to_str - email receivers (comma separated)
        subject - email subject
        html_content - email content
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    if SG_EMAIL_DISABLE:
        print("!!! SendGrid DISABLED !!!")
        return True, None

    # if we are testing functionality - ovewrite from/to
    if SG_TEST_EMAIL:
        print("!!! SendGrid TEST Mode. Overwriting from/to !!!")

        from_email = Email(SG_TEST_FROM)
        to_emails_ = _prep_to_list(SG_TEST_TO)
    else:
        from_email = Email(SG_FROM_EMAIL)
        to_emails_ = _prep_to_list(to_str)

    # excluding emails
    to_emails = [x for x in to_emails_ if x not in SG_EMAIL_EXCL]

    if len(to_emails) == 0:
        return False, "Empty recipient list"

    content = Content("text/html", html_content)

    mail = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=content,
    )

    response = SG_CLIENT.client.mail.send.post(request_body=mail.get())

    success = str(response.status_code).startswith("2")

    return success, response.status_code


def send_summary_email(html_content, upd_timestamp):
    """
    Sends a summary email

    Arguments:
        upd_timestamp - timestamp when eduhub data has been updated
        html_content - email content
    Returns:
        success - flag if the action was succesful
        error - error message
    """

    subject = "EduHub Activity Update (%s UTC)" % (
        upd_timestamp.strftime("%Y-%m-%d %H:%M")
    )

    success, error = send_email(SG_SUMMARY_RECIPIENTS, subject, html_content)

    return success, error
