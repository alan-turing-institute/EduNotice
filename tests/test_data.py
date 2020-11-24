"""
Test data.py module
"""

import os
import pandas as pd

from sqlalchemy import create_engine

from edunotice.constants import (
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME6,
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
)

from edunotice.ingress import update_edu_data
from edunotice.data import (
    get_labs_dict,
    get_courses_dict,
    get_subs_dict,
)

ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME6))


def test_get_courses_labs_subscriptions_dict():
    """
    tests get_labs_dict routine
    """

    # new subscriptions
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    (
        success,
        error,
        lab_dict,
        sub_dict,
        sub_new_list,
        sub_update_list
    ) = update_edu_data(ENGINE, eduhub_df)

    assert success, error
    assert len(sub_new_list) == 2
    assert len(sub_update_list) == 0

    success, error, db_lab_dict = get_labs_dict(ENGINE)
    assert success, error

    assert len(db_lab_dict) == len(lab_dict)

    success, error, db_sub_dict = get_subs_dict(ENGINE)
    assert success, error

    assert len(db_sub_dict) == len(sub_dict)

    success, error, db_course_dict = get_courses_dict(ENGINE)
    assert success, error

    assert len(db_course_dict) == 2
