"""
Module to define the structure of the database.
"""

from sqlalchemy import (
    ForeignKey,
    Column,
    Integer,
    Float,
    String,
    DateTime,
    UniqueConstraint,
    Boolean,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from flask_sqlalchemy import SQLAlchemy

from edunotice.constants import (
    COURSES_TABLE_NAME,
    LABS_TABLE_NAME,
    SUBSCRIPTIONS_TABLE_NAME,
    DETAILS_TABLE_NAME,
    LOGS_TABLE_NAME,
    ID_COL_NAME,
)


SQLA = SQLAlchemy()
BASE = SQLA.Model


class CourseClass(BASE):
    """
    Course class
    """

    __tablename__ = COURSES_TABLE_NAME
    __table_args__ = (UniqueConstraint("name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), onupdate=func.now())

    lab_relationship = relationship("LabClass")


class LabClass(BASE):
    """
    Lab class
    """

    __tablename__ = LABS_TABLE_NAME
    __table_args__ = (UniqueConstraint("course_id", "name"),)

    id = Column(Integer, primary_key=True, autoincrement=True)

    course_id = Column(
        Integer,
        ForeignKey("{}.{}".format(COURSES_TABLE_NAME, ID_COL_NAME)),
        nullable=False,
    )

    name = Column(String(100), nullable=False)

    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), onupdate=func.now())

    details_relationship = relationship("DetailsClass")


class SubscriptionClass(BASE):
    """
    Subscription class
    """

    __tablename__ = SUBSCRIPTIONS_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)

    guid = Column(String(36), nullable=False)

    # notifications
    #   time-based notifications
    expiry_code = Column(Integer)
    expiry_notice_sent = Column(DateTime)

    #  latest information about usage-based notifications
    usage_code = Column(Integer)
    usage_notice_sent = Column(DateTime)

    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), onupdate=func.now())

    details_relationship = relationship("DetailsClass")


class DetailsClass(BASE):
    """
    Subscription details class
    """

    __tablename__ = DETAILS_TABLE_NAME

    # columns
    id = Column(Integer, primary_key=True, autoincrement=True)

    sub_id = Column(
        Integer,
        ForeignKey("{}.{}".format(SUBSCRIPTIONS_TABLE_NAME, ID_COL_NAME)),
        nullable=False,
    )

    lab_id = Column(
        Integer,
        ForeignKey("{}.{}".format(LABS_TABLE_NAME, ID_COL_NAME)),
        nullable=False,
    )

    handout_name = Column(String(100), nullable=False)
    handout_status = Column(String(10), nullable=False)
    handout_budget = Column(Float, nullable=False)
    handout_consumed = Column(Float, nullable=False)

    subscription_name = Column(String(100), nullable=False)
    subscription_status = Column(String(10), nullable=False)
    subscription_expiry_date = Column(DateTime, nullable=False)
    subscription_users = Column(String(10000), nullable=False)

    timestamp_utc = Column(DateTime)

    # creation notifications
    new_flag = Column(Boolean, default=False)
    new_notice_sent = Column(DateTime)

    # update notifications
    update_flag = Column(Boolean, default=False)
    update_notice_sent = Column(DateTime)

    # time-based notifications
    expiry_code = Column(Integer)
    expiry_notice_sent = Column(DateTime)

    # usage-based notifications
    usage_code = Column(Integer)
    usage_notice_sent = Column(DateTime)

    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), onupdate=func.now())

    # arguments
    __table_args__ = (UniqueConstraint("sub_id", "timestamp_utc"),)


class LogsClass(BASE):
    """
    Log class
    """

    __tablename__ = LOGS_TABLE_NAME

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(Integer, nullable=False)
    timestamp_utc = Column(DateTime, nullable=False)

    time_created = Column(DateTime(), server_default=func.now())
    time_updated = Column(DateTime(), onupdate=func.now())
