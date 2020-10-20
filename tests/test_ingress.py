"""
Test ingress.py module
"""

import os
import pandas as pd

from sqlalchemy import create_engine

from edudb.ingress import (
    update_courses,
    update_labs,
    update_subscriptions,
    update_edu_data,
)

from edudb.constants import (
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
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

def test_update_courses():
    """
    tests ingress.update_courses routine
    """

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    # not a dataframe
    succes, error, _ = update_courses(engine, None)
    assert succes is False, error

    # empty dataframe
    succes, error, _ = update_courses(engine, pd.DataFrame())
    assert succes is False, error

    # wrong dataframe
    succes, error, _ = update_courses(engine, wrong_df)
    assert succes is False, error

    # good data
    succes, error, course_dict = update_courses(engine, eduhub_df1)
    assert succes, error
    assert len(course_dict) == 2

    succes, error, course_dict = update_courses(engine, eduhub_df1)
    assert succes, error
    assert len(course_dict) == 2


def test_update_labs():
    """
    tests ingress.update_labs routine
    """

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    # getting the courses
    succes, error, course_dict = update_courses(engine, eduhub_df1)
    assert succes, error
    assert len(course_dict) == 2

    # not a dataframe
    succes, error, _ = update_labs(engine, None, course_dict)
    assert succes is False, error

    # empty dataframe
    succes, error, _ = update_labs(engine, pd.DataFrame(), course_dict)
    assert succes is False, error

    # wrong dataframe
    succes, error, _ = update_labs(engine, wrong_df, course_dict)
    assert succes is False, error

    # good data
    succes, error, lab_dict = update_labs(engine, eduhub_df1, course_dict)
    assert succes, error
    assert len(lab_dict) == 2

    succes, error, lab_dict = update_labs(engine, eduhub_df1, course_dict)
    assert succes, error
    assert len(lab_dict) == 2


def test_update_subscriptions():
    """
    tests ingress.update_subscriptions routine
    """

    engine = create_engine(SQL_CONNECTION_STRING_DB)

    # not a dataframe
    succes, error, _ = update_subscriptions(engine, None)
    assert succes is False, error

    # empty dataframe
    succes, error, _ = update_subscriptions(engine, pd.DataFrame())
    assert succes is False, error

    # wrong dataframe
    succes, error, _ = update_subscriptions(engine, wrong_df)
    assert succes is False, error

    # good data
    succes, error, sub_dict = update_subscriptions(engine, eduhub_df1)
    assert succes, error
    assert len(sub_dict) == 2

    succes, error, sub_dict = update_subscriptions(engine, eduhub_df1)
    assert succes, error
    assert len(sub_dict) == 2

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
