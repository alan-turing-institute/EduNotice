import os

from edunotice.constants import (
    TEST_MODE, 
    SQL_TEST_DBNAME1,
    SQL_TEST_DBNAME2,
    SQL_TEST_DBNAME3,
    SQL_TEST_DBNAME4,
    SQL_TEST_DBNAME5,
    SQL_TEST_DBNAME6,
    SQL_TEST_DBNAME7,
)
from edunotice.db import create_db, drop_db


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    print("pytest_configure: start")
    
    assert TEST_MODE, "Unit tests need to be run in TEST MODE"

    # creates test db 1
    success, log = create_db(db_name=SQL_TEST_DBNAME1)
    assert success, log

    # creates test db 2
    success, log = create_db(db_name=SQL_TEST_DBNAME2)
    assert success, log

    # creates test db 3
    success, log = create_db(db_name=SQL_TEST_DBNAME3)
    assert success, log

    # creates test db 4
    success, log = create_db(db_name=SQL_TEST_DBNAME4)
    assert success, log

    # creates test db 5
    success, log = create_db(db_name=SQL_TEST_DBNAME5)
    assert success, log

    # creates test db 6
    success, log = create_db(db_name=SQL_TEST_DBNAME6)
    assert success, log

    # creates test db 7
    success, log = create_db(db_name=SQL_TEST_DBNAME7)
    assert success, log

    print("pytest_configure: end")


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """

    print("pytest_unconfigure: start")
    
    assert TEST_MODE, "Unit tests need to be run in TEST MODE"

    # drops test db 1
    success, log = drop_db(db_name=SQL_TEST_DBNAME1)
    assert success, log

    # drops test db 2
    success, log = drop_db(db_name=SQL_TEST_DBNAME2)
    assert success, log

    # drops test db 3
    success, log = drop_db(db_name=SQL_TEST_DBNAME3)
    assert success, log

    # drops test db 4
    success, log = drop_db(db_name=SQL_TEST_DBNAME4)
    assert success, log

    # drops test db 5
    success, log = drop_db(db_name=SQL_TEST_DBNAME5)
    assert success, log

    # drops test db 6
    success, log = drop_db(db_name=SQL_TEST_DBNAME6)
    assert success, log

    # drops test db 7
    success, log = drop_db(db_name=SQL_TEST_DBNAME7)
    assert success, log

    print("pytest_unconfigure: end")
