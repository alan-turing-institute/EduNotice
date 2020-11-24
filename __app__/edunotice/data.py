"""
Data module.

"""

from edunotice.db import session_open, session_close

from edunotice.structure import LabClass, CourseClass, SubscriptionClass


def get_labs_dict(engine):
    """
    Returns a dictionary containing all labs and their internal id numbers.

    Arguments:
        engine - an sql engine instance
    Returns:
        success - flag if the action was succesful
        error - error message
        labs_dict - lab name/internal id dictionary
    """

    session = session_open(engine)

    labs_dict = (
        session.query(LabClass)
        .with_entities(LabClass.id, LabClass.name)
        .all()
    )

    session.expunge_all()

    session_close(session)

    return True, None, labs_dict


def get_courses_dict(engine):
    """
    Returns a dictionary containing all courses and their internal id numbers.

    Arguments:
        engine - an sql engine instance
    Returns:
        success - flag if the action was succesful
        error - error message
        courses_dict - lab name/internal id dictionary
    """

    session = session_open(engine)

    courses_dict = (
        session.query(CourseClass)
        .with_entities(CourseClass.id, CourseClass.name)
        .all()
    )

    session.expunge_all()

    session_close(session)

    return True, None, courses_dict


def get_subs_dict(engine):
    """
    Returns a dictionary containing all subscription ids and their internal id numbers.

    Arguments:
        engine - an sql engine instance
    Returns:
        success - flag if the action was succesful
        error - error message
        subs_dict - subscription id/internal id dictionary
    """

    session = session_open(engine)

    subs_dict = (
        session.query(SubscriptionClass)
        .with_entities(SubscriptionClass.guid, SubscriptionClass.id)
        .all()
    )

    session.expunge_all()

    session_close(session)

    return True, None, subs_dict
