# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pytest
import datetime
import contextlib
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from nva.psyquizz import Base
from nva.psyquizz.models import *
from nva.psyquizz.session import file_session_wrapper
from nva.psyquizz.wsgi import routing
from zope.testbrowser.wsgi import Browser


@pytest.fixture(scope='session')
def engine():
    DB_URI = 'file::memory:?cache=shared'
    PY2 = sys.version_info.major == 2
    if PY2:
        params = {}
    else:
        params = {'uri': True}

    creator = lambda: sqlite3.connect(DB_URI, **params)
    return create_engine('sqlite:///:memory:', creator=creator)


@pytest.fixture(scope='function')
def dbsession(engine, request):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    Base.metadata.create_all(engine)

    def teardown():
        Base.metadata.drop_all(engine)
        connection.close()

    request.addfinalizer(teardown)
    return transaction, session


@pytest.fixture(scope='function')
def session_with_content(engine, request):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    Base.metadata.create_all(engine)
    
    account = Account(
        email="ck@novareto.de",
        name="Christian Klinger",
        password="TEST",
        activation="BLA",
        activated=datetime.date.today(),
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
        company_id=1,
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
    session.commit()
    
    def teardown():
        Base.metadata.drop_all(engine)
        connection.close()

    request.addfinalizer(teardown)
    return transaction, session


@pytest.fixture(scope='session')
def browser(engine, zcml):

    wsgi_app = routing(
        conf=None, files=None, session_key='session',
        **{'langs': 'de,fr', 'zcml': zcml, 'name': 'school',
           'engine': engine})
    app = file_session_wrapper(wsgi_app, None, **{'session_key': 'session'})

    def open_url(url):
        return Browser(url, wsgi_app=app)
    return open_url
