"""
Test ingress.py module
"""

import os
import pandas as pd

from sqlalchemy import create_engine

from edunotice.ingress import (
    _update_courses,
    _update_labs,
    _update_subscriptions,
    _update_details,
    update_edu_data,
)

from edunotice.constants import (
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
    CONST_TEST2_FILENAME,
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME1,
)

# wrong dataframe
wrong_df = pd.DataFrame(
    {
        "name": ["Jason", "Molly", "Tina", "Jake", "Amy"],
        "year": [2012, 2012, 2013, 2014, 2014],
        "reports": [4, 24, 31, 2, 3],
    },
    index=["Cochice", "Pima", "Santa Cruz", "Maricopa", "Yuma"],
)

# good data
file_path1 = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
eduhub_df1 = pd.read_csv(file_path1)

ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME1))


def test_update_courses():
    """
    tests ingress._update_courses routine
    """

    # wrong dataframe
    success, error, _ = _update_courses(ENGINE, wrong_df)
    assert success is False, error

    # good data
    success, error, course_dict = _update_courses(ENGINE, eduhub_df1)
    assert success, error
    assert len(course_dict) == 2

    success, error, course_dict = _update_courses(ENGINE, eduhub_df1)
    assert success, error
    assert len(course_dict) == 2


def test_update_labs():
    """
    tests ingress._update_labs routine
    """

    # getting the courses
    success, error, course_dict = _update_courses(ENGINE, eduhub_df1)
    assert success, error
    assert len(course_dict) == 2

    # wrong dataframe
    success, error, _ = _update_labs(ENGINE, wrong_df, course_dict)
    assert success is False, error

    # good data
    success, error, lab_dict = _update_labs(ENGINE, eduhub_df1, course_dict)
    assert success, error
    assert len(lab_dict) == 2

    success, error, lab_dict = _update_labs(ENGINE, eduhub_df1, course_dict)
    assert success, error
    assert len(lab_dict) == 2


def test_update_subscriptions():
    """
    tests ingress._update_subscriptions routine
    """

    # wrong dataframe
    success, error, _ = _update_subscriptions(ENGINE, wrong_df)
    assert success is False, error

    # good data
    success, error, sub_dict = _update_subscriptions(ENGINE, eduhub_df1)
    assert success, error
    assert len(sub_dict) == 2

    success, error, sub_dict = _update_subscriptions(ENGINE, eduhub_df1)
    assert success, error
    assert len(sub_dict) == 2


def test_update_details_1():
    """
    tests ingress._update_details routine

    2 new subscriptions
    """

    # getting the courses
    success, error, course_dict = _update_courses(ENGINE, eduhub_df1)
    assert success, error
    assert len(course_dict) == 2

    # getting the labs
    success, error, lab_dict = _update_labs(ENGINE, eduhub_df1, course_dict)
    assert success, error
    assert len(lab_dict) == 2

    # getting the subscriptions
    success, error, sub_dict = _update_subscriptions(ENGINE, eduhub_df1)
    assert success, error
    assert len(sub_dict) == 2

    # 2 new subscriptions
    success, error, new_list, update_list = _update_details(
        ENGINE, eduhub_df1, lab_dict, sub_dict
    )

    assert success, error
    assert len(new_list) == 2
    assert len(update_list) == 0


def test_update_details_2():
    """
    tests ingress._update_details routine

    1 update
    """

    eduhub_df_local = pd.read_csv(
        os.path.join(CONST_TEST_DIR_DATA, CONST_TEST2_FILENAME)
    )

    # getting the courses
    success, error, course_dict = _update_courses(ENGINE, eduhub_df_local)
    assert success, error
    assert len(course_dict) == 2

    # getting the labs
    success, error, lab_dict = _update_labs(
        ENGINE, eduhub_df_local, course_dict
    )
    assert success, error
    assert len(lab_dict) == 2

    # getting the subscriptions
    success, error, sub_dict = _update_subscriptions(ENGINE, eduhub_df_local)
    assert success, error
    assert len(sub_dict) == 3

    success, error, new_list, update_list = _update_details(
        ENGINE, eduhub_df_local, lab_dict, sub_dict
    )

    assert success, error
    assert len(new_list) == 1
    assert len(update_list) == 2


def test_update_edu_data():
    """
    tests ingress.update_edu_data routine
    """

    # not a dataframe
    (
        success,
        error,
        _,
        _,
        sub_new_list,
        sub_update_list
    ) = update_edu_data(ENGINE, None)
    assert success is False, error

    # empty dataframe
    success, error, _, _, sub_new_list, sub_update_list = update_edu_data(
        ENGINE, pd.DataFrame()
    )
    assert success is False, error

    # real data
    success, error, _, _, sub_new_list, sub_update_list = update_edu_data(
        ENGINE, eduhub_df1
    )

    assert success, error
    assert len(sub_new_list) == 0
    assert len(sub_update_list) == 2
