"""
Data ingress module.

"""

from datetime import datetime, timezone
import pandas as pd

from sqlalchemy import desc, func

from edunotice.db import (
    session_open,
    session_close,
)

from edunotice.structure import (
    CourseClass,
    LabClass,
    SubscriptionClass,
    DetailsClass,
    LogsClass,
)

from edunotice.constants import (
    CONST_PD_COL_COURSE_NAME,
    CONST_PD_COL_LAB_NAME,
    CONST_PD_COL_HANDOUT_NAME,
    CONST_PD_COL_HANDOUT_BUDGET,
    CONST_PD_COL_HANDOUT_CONSUMED,
    CONST_PD_COL_HANDOUT_STATUS,
    CONST_PD_COL_SUB_ID,
    CONST_PD_COL_CRAWL_TIME_UTC,
    CONST_PD_COL_SUB_NAME,
    CONST_PD_COL_SUB_STATUS,
    CONST_PD_COL_SUB_EXPIRY_DATE,
    CONST_PD_COL_SUB_USERS,
    CONST_LOG_CODE_SUCCESS,
)

from edunotice.notifications import details_changed

# lambda function to convert amount in dollars to a float
CONVERT_LAMBDA = lambda x: float(x.replace("$", "").replace(",", ""))


def _check_df(eduhub_df):
    """
    Checks if eduhub_df exists and not empty

    Arguments:
        eduhub_df - pandas dataframe with the eduhub crawl data
    Returns:
        success - flag if the action was succesful
        error - error message
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
    Updates the database with the eduhub crawl data. If a course, lab or handout/subscription is
        not found, new one is created. Updated data is added as new rows in the tables.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
    Returns:
        success - flag if the action was succesful
        error - error message
        lab_dict - lab name/internal id dictionary
        sub_dict - subscription id/internal id dictionar
        sub_new_list - a list of details of new subscriptions
        sub_upd_list - a list of tuples (before, after) of subscription details
        success_timestamp_utc - timestamp of successful edu data update
    """

    course_dict = None
    lab_dict = None
    sub_dict = None
    sub_new_list = None
    sub_upd_list = None
    success_timestamp_utc = None

    success, error = _check_df(eduhub_df)

    if success:
        # order data by 'Subscription id' and 'Crawl time utc'
        eduhub_df.sort_values(
            by=[CONST_PD_COL_SUB_ID, CONST_PD_COL_CRAWL_TIME_UTC], inplace=True
        )

        # getting unique courses and making sure that they are in the database
        success, error, course_dict = _update_courses(engine, eduhub_df)

    if success:
        # getting unique labs and making sure that they are in the database
        success, error, lab_dict = _update_labs(engine, eduhub_df, course_dict)

    if success:
        # getting unique subscriptions and making sure that they are in the database
        success, error, sub_dict = _update_subscriptions(engine, eduhub_df)

    if success:
        # updating details
        success, error, sub_new_list, sub_upd_list = _update_details(
            engine, eduhub_df, lab_dict, sub_dict
        )

    if success:
        # log the successful update
        success, error, success_timestamp_utc = _new_log(engine)

    return success, error, lab_dict, sub_dict, sub_new_list, sub_upd_list, success_timestamp_utc


def _new_log(engine):
    """
    Logs successful update of edu_data

    Arguments:
        engine - an sql engine instance
    Returns:
        success - flag if the action was succesful
        error - error message
        timestamp_utc - timestamp value
    """

    session = session_open(engine)

    timestamp_utc = datetime.now(timezone.utc)

    new_log = LogsClass(code=CONST_LOG_CODE_SUCCESS, timestamp_utc=timestamp_utc,)

    session.add(new_log)

    session.flush()
    #session.commit()

    session_close(session)

    return True, None, timestamp_utc


def get_latest_log_timestamp(engine):
    """
    Gets the latest timestamp value.

    Arguments:
        engine - an sql engine instance
    Returns:
        success - flag if the action was succesful
        error - error message
        timestamp_utc - timestamp value
    """

    session = session_open(engine)

    timestamp = session.query(func.max(LogsClass.timestamp_utc)).first()[0]
    
    if timestamp is not None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    session.expunge_all()
    session_close(session)

    return True, None, timestamp


def _update_courses(engine, eduhub_df):
    """
    Updates the database with the courses eduhub crawl data and returns a
        dictionary containing all courses and their internal id numbers.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
    Returns:
        success - flag if the action was succesful
        error - error message
        course_dict - course name/internal id dictionary
    """

    course_dict = {}

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
            #session.commit() 

            course_dict.update({course_name: new_course.id})

    session_close(session)

    return True, None, course_dict


def _update_labs(engine, eduhub_df, course_dict):
    """
    Updates the database with the labs eduhub crawl data and returns a
        dictionary containing all labs and their internal id numbers.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
        course_dict - course name/internal id dictionary
    Returns:
        success - flag if the action was succesful
        error - error message
        lab_dict - lab name/internal id dictionary
    """

    lab_dict = {}

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
            #session.commit()

            lab_dict.update({(course_name, lab_name): new_lab.id})
        else:
            lab_dict.update({(course_name, lab_name): lab_id})

    session_close(session)

    return True, None, lab_dict


def _update_subscriptions(engine, eduhub_df):
    """
    Updates the database with the subscriptions eduhub crawl data and returns a
        dictionary containing all subscription ids and their internal id numbers.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
    Returns:
        success - flag if the action was succesful
        error - error message
        sub_dict - subscription id/internal id dictionary
    """

    sub_dict = {}

    try:
        unique_subscription_ids = eduhub_df[CONST_PD_COL_SUB_ID].unique()
    except KeyError as exception:
        return False, exception, sub_dict

    if len(unique_subscription_ids) == 0:
        return False, "dataframe does not contain course names", sub_dict

    session = session_open(engine)

    # get the internal ids of the subscriptions that are already in the database
    query_result = (
        session.query(SubscriptionClass)
        .filter(SubscriptionClass.guid.in_(unique_subscription_ids))
        .with_entities(SubscriptionClass.guid, SubscriptionClass.id)
        .all()
    )

    for (sub_guid, sub_id) in query_result:
        sub_dict.update({sub_guid: sub_id})

    # insert new subscriptions in to the database
    for sub_guid in unique_subscription_ids:
        if sub_guid not in sub_dict.keys():
            # new course -> insert to the database
            new_subscription = SubscriptionClass(guid=sub_guid,)

            session.add(new_subscription)
            session.flush()
            #session.commit()

            sub_dict.update({sub_guid: new_subscription.id})

    session_close(session)

    return True, None, sub_dict


def _update_details(engine, eduhub_df, lab_dict, sub_dict):
    """
    Updates the database with the subscription/handouts details eduhub crawl data.

    Arguments:
        engine - an sql engine instance
        eduhub_df - pandas dataframe with the eduhub crawl data
        lab_dict - lab name /internal id dictionary
        sub_dict - subscription id /internal id dictionary
    Returns:
        success - flag if the action was succesful
        error - error message
        new_list - a list of details of new subscriptions
        update_list - a list of tuples (before, after) of subscription details
    """

    new_list = []
    update_list = []

    session = session_open(engine)

    for sub_guid in sub_dict.keys():

        # selecting all the entries for a particular subscription and
        #    sorting them by the crawl time in ascending order
        sub_eduhub_df = eduhub_df[
            eduhub_df[CONST_PD_COL_SUB_ID] == sub_guid
        ].sort_values([CONST_PD_COL_CRAWL_TIME_UTC])

        sub_id = sub_dict[sub_guid]

        # get the latest details before
        prev_details = (
            session.query(DetailsClass)
            .filter(DetailsClass.sub_id == sub_id)
            .order_by(desc(DetailsClass.timestamp_utc))
            .first()
        )

        if prev_details is not None:
            session.expunge(prev_details)

        # appending details
        for _, row in sub_eduhub_df.iterrows():
            
            crawl_time = row[CONST_PD_COL_CRAWL_TIME_UTC]

            if (
                session.query(DetailsClass)
                    .filter(
                        DetailsClass.sub_id == sub_id,
                        DetailsClass.timestamp_utc == crawl_time,
                    )
                    .scalar()
                    is None
            ):

                if type(row[CONST_PD_COL_SUB_USERS]) is str:
                    sub_users = ", ".join(eval(row[CONST_PD_COL_SUB_USERS]))
                elif type(row[CONST_PD_COL_SUB_USERS]) is list:
                    sub_users = ", ".join(row[CONST_PD_COL_SUB_USERS])
                else:
                    sub_users = ''
               
                # adds new record to the database
                new_sub_detail = DetailsClass(
                    sub_id=sub_id,
                    lab_id=lab_dict[
                        (row[CONST_PD_COL_COURSE_NAME], row[CONST_PD_COL_LAB_NAME])
                    ],
                    handout_name=row[CONST_PD_COL_HANDOUT_NAME],
                    handout_status=row[CONST_PD_COL_HANDOUT_STATUS],
                    handout_budget=CONVERT_LAMBDA(row[CONST_PD_COL_HANDOUT_BUDGET]),
                    handout_consumed=CONVERT_LAMBDA(row[CONST_PD_COL_HANDOUT_CONSUMED]),
                    subscription_name=row[CONST_PD_COL_SUB_NAME],
                    subscription_status=row[CONST_PD_COL_SUB_STATUS],
                    subscription_expiry_date=datetime.strptime(row[CONST_PD_COL_SUB_EXPIRY_DATE], "%Y-%m-%d"),
                    subscription_users=sub_users,
                    timestamp_utc=crawl_time,
                    new_flag=(prev_details is None),
                )

                if (prev_details is not None) and details_changed(prev_details, new_sub_detail):
                    new_sub_detail.update_flag = True

                session.add(new_sub_detail)
                session.flush()
                #session.commit() 
                
        # get the latest details after
        latest_details = (
            session.query(DetailsClass)
            .filter(DetailsClass.sub_id == sub_id)
            .order_by(desc(DetailsClass.timestamp_utc))
            .first()
        )
        session.expunge(latest_details)

        if prev_details is None:
            new_list.append(latest_details)
        else:
            update_list.append((prev_details, latest_details))

            # if handout_budget has changed, nullify usage_code and usage_notice_sent
            if prev_details.handout_budget != latest_details.handout_budget:

                session.query(SubscriptionClass).filter(
                    SubscriptionClass.id == latest_details.sub_id
                ).update(
                    {
                        "usage_code": None,
                        "usage_notice_sent": None,
                    }
                )
                session.commit()

            # if subscription_expiry_date has changed, nullify expiry_code and expiry_notice_sent
            if prev_details.subscription_expiry_date != latest_details.subscription_expiry_date:

                session.query(SubscriptionClass).filter(
                    SubscriptionClass.id == latest_details.sub_id
                ).update(
                    {
                        "expiry_code": None,
                        "expiry_notice_sent": None,
                    }
                )
                session.commit()

    session_close(session)

    return True, None, new_list, update_list
