# -*- coding: utf-8 -*-

from shortid import ShortId
from datetime import datetime
from nva.psyquizz import Base
from nva.psyquizz.models.interfaces import IQuizz, IStudent
from sqlalchemy import *
from sqlalchemy.event import listens_for
from uvclight import getRequest
from zope.component import getUtility
from zope.interface import implementer, directlyProvides
from zope.location import Location

from ..interfaces import ICompanyRequest


@implementer(IQuizz, IStudent)
class Student(Base, Location):

    __tablename__ = 'students'

    access = Column('access', String, primary_key=True)
    email = Column('email', String)

    # Relationships
    course_id = Column(Integer, ForeignKey('courses.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))

    # Origin
    anonymous = Column('anonymous', Boolean)

    # Quizz
    quizz_type = Column('quizz_type', String)
    completion_date = Column('completion_date', DateTime)

    @property
    def id(self):
        return self.access

    @staticmethod
    def generate_access():
        sid = ShortId()
        return unicode(sid.generate())

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


@listens_for(Student, 'load')
def student_quizz(target, context):
    iface = getUtility(IQuizz, name=target.quizz_type).__schema__
    directlyProvides(target, iface)
