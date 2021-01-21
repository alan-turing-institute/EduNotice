"""
DB management module.

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, drop_database

from edunotice.constants import (
    SQL_CONNECTION_STRING,
    SQL_CONNECTION_STRING_DB,
    SQL_CONNECTION_STRING_DEFAULT,
    SQL_DBNAME,
)

from edunotice.structure import BASE


def create_db(db_name=None):
    """
    Creates a new database.

    Arguments:
        db_name - name of the new database
    Returns:
        success - success flag
        error - error message
    """

    # if db_name is not specified, use the default values
    if db_name is None:
        new_db_name = SQL_DBNAME
        new_db_sql_con_string = SQL_CONNECTION_STRING_DB
    else:
        new_db_name = db_name
        new_db_sql_con_string = "%s/%s" % (SQL_CONNECTION_STRING, db_name)

    if not database_exists(new_db_sql_con_string):

        try:
            engine = create_engine(SQL_CONNECTION_STRING_DEFAULT)

            conn = engine.connect()

            conn.execute("commit")

            conn.execute("create database " + new_db_name)

            engine = create_engine(new_db_sql_con_string)

            BASE.metadata.create_all(engine)

            conn.close()
        except Exception:
            return False, "Error while creating a new database"
    else:
        return False, "Database already exists."

    return True, None


def drop_db(db_name=None):
    """
    Drops the default database.

    Arguments:
        db_name - name of the new database
    Returns:
        success - success flag
        error - error message
    """

    # if db_name is not specified, use the default value
    if db_name is None:
        del_db_sql_con_string = SQL_CONNECTION_STRING_DB
    else:
        del_db_sql_con_string = "%s/%s" % (SQL_CONNECTION_STRING, db_name)

    drop_database(del_db_sql_con_string)

    return True, None


def session_open(engine):
    """
    Opens a new connection/session to the db and binds the engine

    Arguments:
        engine: the connected engine
    """

    Session = sessionmaker()
    Session.configure(bind=engine)

    return Session()


def session_close(session):
    """
    Closes the session
    Arguments:
        session: session
    """

    session.commit()
    session.close()
