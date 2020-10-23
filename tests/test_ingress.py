"""
Test ingress.py module
"""

import os
import pandas as pd

from sqlalchemy import create_engine

from edudb.ingress import (
    _update_courses,
    _update_labs,
    _update_subscriptions,
    _update_details,
    update_edu_data,
)

from edudb.constants import (
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
    CONST_TEST2_FILENAME,
    SQL_CONNECTION_STRING_DB
)

# wrong dataframe
wrong_df = pd.DataFrame({
        'name': ['Jason', 'Molly', 'Tina', 'Jake', 'Amy'],
        'year': [2012, 2012, 2013, 2014, 2014],
        'reports': [4, 24, 31, 2, 3]
    },
    index=['Cochice', 'Pima', 'Santa Cruz', 'Maricopa', 'Yuma']
)

# good data
file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
eduhub_df1 = pd.read_csv(file_path)

engine = create_engine(SQL_CONNECTION_STRING_DB)


def test_update_courses():
    """
    tests ingress._update_courses routine
    """

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    # wrong dataframe
    succes, error, _ = _update_courses(engine, wrong_df)
    assert succes is False, error

    # good data
    succes, error, course_dict = _update_courses(engine, eduhub_df1)
    assert succes, error
    assert len(course_dict) == 2

    succes, error, course_dict = _update_courses(engine, eduhub_df1)
    assert succes, error
    assert len(course_dict) == 2


def test_update_labs():
    """
    tests ingress._update_labs routine
    """

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    # getting the courses
    succes, error, course_dict = _update_courses(engine, eduhub_df1)
    assert succes, error
    assert len(course_dict) == 2

    # wrong dataframe
    succes, error, _ = _update_labs(engine, wrong_df, course_dict)
    assert succes is False, error

    # good data
    succes, error, lab_dict = _update_labs(engine, eduhub_df1, course_dict)
    assert succes, error
    assert len(lab_dict) == 2

    succes, error, lab_dict = _update_labs(engine, eduhub_df1, course_dict)
    assert succes, error
    assert len(lab_dict) == 2


def test_update_subscriptions():
    """
    tests ingress._update_subscriptions routine
    """

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    # wrong dataframe
    succes, error, _ = _update_subscriptions(engine, wrong_df)
    assert succes is False, error

    # good data
    succes, error, sub_dict = _update_subscriptions(engine, eduhub_df1)
    assert succes, error
    assert len(sub_dict) == 2

    succes, error, sub_dict = _update_subscriptions(engine, eduhub_df1)
    assert succes, error
    assert len(sub_dict) == 2


def test_update_details_1():
    """
    tests ingress._update_details routine

    2 new subscriptions
    """

    # getting the courses
    succes, error, course_dict = _update_courses(engine, eduhub_df1)
    assert succes, error
    assert len(course_dict) == 2

    # getting the labs
    succes, error, lab_dict = _update_labs(engine, eduhub_df1, course_dict)
    assert succes, error
    assert len(lab_dict) == 2

    # getting the subscriptions
    succes, error, sub_dict = _update_subscriptions(engine, eduhub_df1)
    assert succes, error
    assert len(sub_dict) == 2

    # 2 new subscriptions
    succes, error, new_list, update_list = _update_details(engine, eduhub_df1, lab_dict, sub_dict)

    assert succes, error
    assert len(new_list) == 2
    assert len(update_list) == 0


def test_update_details_2():
    """
    tests ingress._update_details routine

    1 update
    """

    eduhub_df_local = pd.read_csv(
        os.path.join(CONST_TEST_DIR_DATA, CONST_TEST2_FILENAME))

    # getting the courses
    succes, error, course_dict = _update_courses(engine, eduhub_df_local)
    assert succes, error
    assert len(course_dict) == 1

    # getting the labs
    succes, error, lab_dict = _update_labs(engine, eduhub_df_local, course_dict)
    assert succes, error
    assert len(lab_dict) == 1

    # getting the subscriptions
    succes, error, sub_dict = _update_subscriptions(engine, eduhub_df_local)
    assert succes, error
    assert len(sub_dict) == 1

    succes, error, new_list, update_list = _update_details(engine, eduhub_df_local, lab_dict, sub_dict)

    assert succes, error
    assert len(new_list) == 0
    assert len(update_list) == 1


def test_update_edu_data():
    """
    tests ingress.update_edu_data routine
    """

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    # not a dataframe
    succes, error = update_edu_data(engine, None)
    assert succes is False, error

    # empty dataframe
    succes, error = update_edu_data(engine, pd.DataFrame())
    assert succes is False, error

    # real data
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    succes, error = update_edu_data(engine, eduhub_df)

    assert succes, error
