"""
Test sender.py module
"""

import pytest

from edunotice.sender import (
   send_email
)

from edunotice.constants import(
    SG_FROM_EMAIL,
    SG_TEST_EMAIL,
)

TEST_EMAIL_API = pytest.mark.skipif(not SG_TEST_EMAIL, reason="Testing Email API is switched off")


@TEST_EMAIL_API
def test_send_email1():
    """
    Tests send_email function.

    """

    subject = "Test message"
    html_content = "<html><body><p>This is a test message!</p></body></html>"

    # One recipient
    success, error = send_email(SG_FROM_EMAIL, subject, html_content)
    assert success, error
