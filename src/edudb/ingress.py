"""
Data ingress module.

"""

import pandas as pd

from edudb.db import (
    session_open,
    session_close,
)

from edudb.structure import CourseClass, LabClass

from edudb.constants import (
    CONST_PD_COL_COURSE_NAME,
    CONST_PD_COL_LAB_NAME,
    CONST_PD_COL_SUB_ID,
    CONST_PD_COL_CRAWL_TIME_UTC,
)


def check_df(eduhub_df):
    """
    Check if the argument passed is not empty pandas dataframe
    """

    # Checks if df exists
    if not isinstance(eduhub_df, pd.DataFrame):
        return False, "Not a pandas dataframe"

    # Checks if df is empty
    if eduhub_df.empty:
        return False, "Dataframe empty"

    return True, None


def update_edu_data(engine, eduhub_df):
    """
    Updates database with the eduhub crawl data. If course, lab, handout/subscriptions are
        not found, new ones are created. Updated data is added as new rows in the tables.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
    """

    success, error = check_df(eduhub_df)

    if not success:
        return success, error

    # order data by 'Subscription id' and 'Crawl time utc'
    eduhub_df.sort_values(
        by=[CONST_PD_COL_SUB_ID, CONST_PD_COL_CRAWL_TIME_UTC], inplace=True
    )

    # getting unique courses and checking if they are in the database
    succes, error, course_dict = update_courses(engine, eduhub_df)

    if not succes:
        return success, error

    # getting unique labs and checking if they are in the database
    succes, error, lab_dict = update_labs(engine, eduhub_df, course_dict)

    if not succes:
        return success, error

    return True, None


def update_courses(engine, eduhub_df):
    """
    Updates database with the courses eduhub crawl data and returns a
        dictionary containing all courses and their internal id numbers.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
    Returns:
        success - flag if the action was succesful
        error - error message
        course_dict - course name /internal id dictionary
    """

    course_dict = {}

    success, error = check_df(eduhub_df)

    if not success:
        return success, error, course_dict

    try:
        unique_courses = eduhub_df[CONST_PD_COL_COURSE_NAME].unique()
    except KeyError as exception:
        return False, exception, course_dict

    if len(unique_courses) == 0:
        return False, "dataframe does not contain course names", course_dict

    session = session_open(engine)

    # get the ids of the courses that are already in the database
    query_result = (
        session.query(CourseClass)
        .filter(CourseClass.name.in_(unique_courses))
        .with_entities(CourseClass.name, CourseClass.id)
        .all()
    )

    for (course_name, course_id) in query_result:
        course_dict.update({course_name: course_id})

    # insert new courses in to the database
    for course_name in unique_courses:
        if course_name not in course_dict.keys():
            # new course -> insert to the database
            new_course = CourseClass(name=course_name,)

            session.add(new_course)
            session.flush()

            course_dict.update({course_name: new_course.id})

    session_close(session)

    return True, None, course_dict


def update_labs(engine, eduhub_df, course_dict):
    """
    Updates database with the labs eduhub crawl data and returns a
        dictionary containing all labs and their internal id numbers.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
        course_dict - course name /internal id dictionary
    Returns:
        success - flag if the action was succesful
        error - error message
        lab_dict - lab name /internal id dictionary
    """

    lab_dict = {}

    success, error = check_df(eduhub_df)

    if not success:
        return success, error, lab_dict

    # unique course/lab combinations
    try:
        labs = eduhub_df[[CONST_PD_COL_COURSE_NAME, CONST_PD_COL_LAB_NAME]]
        unique_labs = labs.drop_duplicates()
    except KeyError as exception:
        return False, exception, lab_dict

    session = session_open(engine)

    # inserting new labs
    for _, row in unique_labs.iterrows():
        course_name = row[CONST_PD_COL_COURSE_NAME]
        lab_name = row[CONST_PD_COL_LAB_NAME]

        course_id = course_dict[course_name]

        try:
            lab_id = (
                session.query(LabClass)
                .filter(LabClass.course_id == course_id)
                .filter(LabClass.name == lab_name)
                .first()
                .id
            )
        except AttributeError as exception:
            lab_id = 0

        # create new lab
        if lab_id == 0:
            # new lab -> insert to the database
            new_lab = LabClass(name=lab_name, course_id=course_id,)

            session.add(new_lab)
            session.flush()

            lab_dict.update({(course_name, lab_name): new_lab.id})
        else:
            lab_dict.update({(course_name, lab_name): lab_id})

    session_close(session)

    return True, None, lab_dict


def update_subscriptions(engine, eduhub_df):
    """
    Updates database with the subscriptions eduhub crawl data and returns a
        dictionary containing all subscription ids and their internal id numbers.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
    Returns:
        success - flag if the action was succesful
        error - error message
        sub_dict - subscription id /internal id dictionary
    """

    sub_dict = {}

    success, error = check_df(eduhub_df)

    if not success:
        return success, error, sub_dict

    try:
        unique_subscription_ids = eduhub_df[CONST_PD_COL_SUB_ID].unique()
    except KeyError as exception:
        return False, exception, sub_dict

    if len(unique_subscription_ids) == 0:
        return False, "dataframe does not contain course names", sub_dict

    print(unique_subscription_ids)

    return False, None, sub_dict