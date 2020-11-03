"""
Email sending module
"""

import os
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail

SG_FROM_EMAIL = os.environ.get('ENS_FROM_EMAIL')
SG_SUMMARY_RECIPIENTS = os.environ.get('ENS_SUMMARY_RECIPIENTS')
SG_CLIENT = sendgrid.SendGridAPIClient(api_key=os.environ.get('ENS_EMAIL_API'))

def send_email(to, subject, html_content):
    """
    A function to send an email

    Arguments:
        to - email receivers
        subject - email subject
        html_content - email content
    Returns:
        success - flag if the action was succesful
        error - error message
    """ 

    from_email = Email(SG_FROM_EMAIL)
    to_email = To(to)

    content = Content("text/html", html_content)

    mail = Mail(from_email, to_email, subject, content)
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

    subject = "EduHub Activity Update (%s UTC)" % (upd_timestamp.strftime("%Y-%m-%d %H:%M"))
    
    success, error = send_email(SG_SUMMARY_RECIPIENTS, subject, html_content)

    return success, error


def test_send_email():
    """
    Tests send_email function.

    """

    subject = "Test message"
    html_content = "<html><body><p>This is a test message!</p></body></html>"

    success, error = send_email(SG_FROM_EMAIL, subject, html_content)

    assert success, error
