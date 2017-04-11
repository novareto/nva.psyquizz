# -*- coding: utf-8 -*-

import os
import pytest
import datetime
import transaction
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from nva.psyquizz import Base
from nva.psyquizz.models import *
from nva.psyquizz.session import file_session_wrapper
from nva.psyquizz.wsgi import routing
from zope.testbrowser.wsgi import Browser


@pytest.fixture(scope='session')
def engine():
    return create_engine('sqlite:////tmp/quizz.db')


@pytest.yield_fixture(scope='session')
def tables(engine):
    Base.metadata.create_all(engine.engine)
    yield
    Base.metadata.drop_all(engine.engine)


@pytest.yield_fixture
def dbsession(engine, tables):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield transaction, session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.yield_fixture
def session_with_content(dbsession):
    # do your data injection here
    transaction, session = dbsession
    
    account = Account(
        email="ck@novareto.de",
        name="Christian Klinger",
        password="TEST",
        activation="BLA"
    )

    company = Company(
        id=1,
        name="Novareto",
        mnr="A",
        employees="B",
        exp_db="C",
        type="D",
        account_id=account.email)

    course = Course(
        id=1,
        name="Crash Course",
        startdate=datetime.date.today(),
        company_id=company.id,
        quizz_type="quizz2",
        extra_questions="""To be or not to be ?
""")

    clsession = ClassSession(
        id=1,
        startdate=datetime.date.today(),
        enddate=datetime.date.today() + datetime.timedelta(days=5),
        strategy="",
        company_id=1,
        course_id=1,
        about="A course.",
        )

    student = Student(
        access="ABCD",
        email="christian@novareto.de",
        course_id=1,
        company_id=1,
        session_id=1,
        anonymous=False,
        quizz_type="quizz2",
        completion_date=datetime.date.today() + datetime.timedelta(days=1))

    session.add(account)
    session.add(company)
    session.add(course)
    session.add(clsession)
    session.add(student)

    yield transaction, session


@pytest.fixture(scope='session')
def browser(zcml):
    wsgi_app = routing(
        conf=None, files=None, session_key='session',
        **{'langs': 'de,fr', 'zcml': zcml, 'name': 'test'})
    app = file_session_wrapper(wsgi_app, None, **{'session_key': 'session'})

    def open_url(url):
        return Browser(url, wsgi_app=app)
    return open_url
