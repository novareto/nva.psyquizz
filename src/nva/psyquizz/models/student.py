# -*- coding: utf-8 -*-

import uuid

from ..interfaces import ICompanyRequest
from nva.psyquizz import Base
from nva.psyquizz.models.interfaces import IQuizz, IStudent
from datetime import datetime
from sqlalchemy import *
from zope.interface import implementer
from zope.location import Location
from uvclight import getRequest

@implementer(IQuizz, IStudent)
class Student(Base, Location):

    __tablename__ = 'students'

    access = Column('access', String, primary_key=True)
    email = Column('email', String)

    # Relationships
    course_id = Column(Integer, ForeignKey('courses.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))

    # Quizz
    quizz_type = Column('quizz_type', String)
    completion_date = Column('completion_date', DateTime)

    @property
    def id(self):
        return self.access

    @staticmethod
    def generate_access():
        return unicode(uuid.uuid4())

    def complete_quizz(self):
        self.completion_date = datetime.now()

    @property
    def __name__(self):
        return self.access

    @__name__.setter
    def __name__(self, value):
        pass

    @property
    def isEditable(self):
        request = getRequest()
        return ICompanyRequest.providedBy(request)

    @property
    def isDeletable(self):
        request = getRequest()
        return ICompanyRequest.providedBy(request)
