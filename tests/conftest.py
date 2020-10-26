
from edunotice.constants import (
    TEST_MODE, 
    SQL_TEST_DBNAME1,
    SQL_TEST_DBNAME2,
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

    print("pytest_unconfigure: end")