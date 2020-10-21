
from edudb.constants import TEST_MODE
from edudb.db import create_db, drop_db


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    print("pytest_configure: start")
    
    assert TEST_MODE, "Unit tests need to be run in TEST MODE"

    # creates test db
    success, log = create_db()
    assert success, log

    print("pytest_configure: end")

def pytest_unconfigure(config):
    """
    called before test process is exited.
    """

    print("pytest_unconfigure: start")
    
    assert TEST_MODE, "Unit tests need to be run in TEST MODE"

    # drops test db
    success, log = drop_db()
    assert success, log

    print("pytest_unconfigure: end")