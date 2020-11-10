"""
Test expiry.py module
"""

import datetime

from edunotice.expiry import (
    check_remaining_time
)

from edunotice.constants import (
    CONST_EXPR_CODE_1,
    CONST_EXPR_CODE_7,
    CONST_EXPR_CODE_30,
)

def test_check_remaining_time():

    current_date = datetime.datetime(2020, 11, 10).date()

    # 1 day
    expires, expiry_code = check_remaining_time(datetime.datetime(2020, 11, 9).date(), current_date=current_date)

    assert expires
    assert expiry_code == CONST_EXPR_CODE_1

    # 5 days
    expires, expiry_code = check_remaining_time(datetime.datetime(2020, 11, 5).date(), current_date=current_date)

    assert expires
    assert expiry_code == CONST_EXPR_CODE_7

    # 7 days
    expires, expiry_code = check_remaining_time(datetime.datetime(2020, 11, 3).date(), current_date=current_date)

    assert expires
    assert expiry_code == CONST_EXPR_CODE_7

    # 14 days
    expires, expiry_code = check_remaining_time(datetime.datetime(2020, 10, 27).date(), current_date=current_date)

    assert expires
    assert expiry_code == CONST_EXPR_CODE_30

    # 30 days
    expires, expiry_code = check_remaining_time(datetime.datetime(2020, 10, 11).date(), current_date=current_date)

    assert expires
    assert expiry_code == CONST_EXPR_CODE_30

    # 70 days (longer than 30 days)
    expires, expiry_code = check_remaining_time(datetime.datetime(2020, 9, 1).date(), current_date=current_date)

    assert expires == False
    assert expiry_code is None