"""
Email sending module
"""

import os
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail, Personalization

from edunotice.constants import(
    SG_FROM_EMAIL,
    SG_SUMMARY_RECIPIENTS,
    SG_API_KEY,
)

SG_CLIENT = sendgrid.SendGridAPIClient(api_key=SG_API_KEY)

def send_email(to, subject, html_content):
    """
    A function to send an email

    Arguments:
        to - email receivers (comma separated)
        subject - email subject
        html_content - email content
    Returns:
        success - flag if the action was succesful
        error - error message
    """ 

    if type(to) is list:
        to_arr = to
    else:
        to_arr = [x.strip() for x in to.split(',')]

    to_arr = list(set(to_arr)) # making sure that values are unique

    if len(to_arr) == 0:
        return False, "Empty recipient list"

    to_list = [] 
    for to_arr_el in to_arr:
        to_list.append(To(to_arr_el))

    from_email = Email(SG_FROM_EMAIL)

    content = Content("text/html", html_content)

    mail = Mail(from_email=from_email, to_emails=to_list, subject=subject, html_content=content)

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
