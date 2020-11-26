"""
Test notifications.py module
"""

import os
import pandas as pd

from sqlalchemy import create_engine

from edunotice.ingress import (
    update_edu_data,
)

from edunotice.notifications import (
    indiv_email_new,
    indiv_email_upd,
)

from edunotice.constants import (
    CONST_TEST_DIR_DATA,
    CONST_TEST1_FILENAME,
    CONST_TEST2_FILENAME,
    CONST_TEST3_FILENAME,
    CONST_TEST4_FILENAME,
    CONST_TEST5_FILENAME,
    SQL_CONNECTION_STRING,
    SQL_TEST_DBNAME2,
)

# good data
file_path1 = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
eduhub_df1 = pd.read_csv(file_path1)

ENGINE = create_engine("%s/%s" % (SQL_CONNECTION_STRING, SQL_TEST_DBNAME2))


def test_importing_test_data():
    """
    imports initial test data
    """

    # 2 new
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST1_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    success, error, _, _, sub_new_list, sub_update_list = update_edu_data(
        ENGINE, eduhub_df
    )

    assert success, error
    assert len(sub_new_list) == 2
    assert len(sub_update_list) == 0

    # 2 updates and 1 new
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST2_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    success, error, _, _, sub_new_list, sub_update_list = update_edu_data(
        ENGINE, eduhub_df
    )

    assert success, error
    assert len(sub_new_list) == 1
    assert len(sub_update_list) == 2

    # 1 update
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST3_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    # putting the data into the database
    success, error, _, _, sub_new_list, sub_update_list = update_edu_data(
        ENGINE, eduhub_df
    )

    assert success, error
    assert len(sub_new_list) == 0
    assert len(sub_update_list) == 3


def test_indiv_email_new():
    """
    test new individual emails
    """

    # real data
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST4_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    success, error, lab_dict, sub_dict, sub_new_list, sub_update_list = update_edu_data(
        ENGINE, eduhub_df
    )

    assert success, error
    assert len(sub_new_list) == 2
    assert len(sub_update_list) == 0

    success, error, html_content = indiv_email_new(lab_dict, sub_dict, sub_new_list[0])

    assert success, error
    assert len(html_content) == 3811

    success, error, html_content = indiv_email_new(lab_dict, sub_dict, sub_new_list[1])

    assert success, error
    assert len(html_content) == 4758


def test_indiv_email_update():
    """
    test update individual emails
    """

    # real data
    file_path = os.path.join(CONST_TEST_DIR_DATA, CONST_TEST5_FILENAME)
    eduhub_df = pd.read_csv(file_path)

    success, error, lab_dict, sub_dict, sub_new_list, sub_update_list = update_edu_data(
        ENGINE, eduhub_df
    )

    for asd in sub_new_list:
        print(asd.subscription_name)

    assert success, error
    assert len(sub_new_list) == 0
    assert len(sub_update_list) == 2

    success, error, html_content = indiv_email_upd(
        lab_dict, sub_dict, sub_update_list[0]
    )

    assert success, error
    assert len(html_content) == 3451

    success, error, html_content = indiv_email_upd(
        lab_dict, sub_dict, sub_update_list[1]
    )

    assert success, error
    assert len(html_content) == 3212
