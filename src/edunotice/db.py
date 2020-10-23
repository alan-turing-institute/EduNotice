"""
DB management module.

"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, drop_database

from edunotice.constants import (
    SQL_CONNECTION_STRING_DB,
    SQL_CONNECTION_STRING_DEFAULT,
    SQL_DBNAME,
)

from edunotice.structure import BASE


def create_db():
    """
    Creates a new database.
    """

    if not database_exists(SQL_CONNECTION_STRING_DB):

        try:
            engine = create_engine(SQL_CONNECTION_STRING_DEFAULT)

            conn = engine.connect()

            conn.execute("commit")

            conn.execute("create database " + SQL_DBNAME)

            engine = create_engine(SQL_CONNECTION_STRING_DB)

            BASE.metadata.create_all(engine)

            conn.close()
        except:
            return False, "Error while creating a new database"
    else:
        return False, "Database already exists."

    return True, None


def drop_db():
    """
    Drops the default database.
    """

    drop_database(SQL_CONNECTION_STRING_DB)

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