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

    labs_list = (
        session.query(LabClass)
        .with_entities(LabClass.id, LabClass.course_id, LabClass.name)
        .all()
    )

    courses_list = (
        session.query(CourseClass)
        .with_entities(CourseClass.id, CourseClass.name)
        .all()
    )

    session.expunge_all()

    session_close(session)

    courses_dict = {}
    for (course_id, course_name) in courses_list:
        courses_dict.update({course_id: course_name})

    labs_dict = {}

    for (lab_id, course_id, lab_name) in labs_list:

        course_name = courses_dict[course_id]

        labs_dict.update({(course_name, lab_name): lab_id})

    return True, None, labs_dict


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

    subs_list = (
        session.query(SubscriptionClass)
        .with_entities(SubscriptionClass.guid, SubscriptionClass.id)
        .all()
    )

    session.expunge_all()

    session_close(session)

    subs_dict = {}

    for (sub_guid, sub_id) in subs_list:
        subs_dict.update({sub_guid: sub_id})

    return True, None, subs_dict
