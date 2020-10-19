"""
DB management module.

"""

from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists

from edudb.constants import (
    SQL_CONNECTION_STRING_DB,
    SQL_CONNECTION_STRING_DEFAULT,
    SQL_DBNAME
)

from edudb.structure import BASE

def create_database():
    """
    Creates new database.
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