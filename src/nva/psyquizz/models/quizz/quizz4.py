# -*- coding: utf-8 -*-


from .quizz2 import Quizz2, IQuizz2
from .. import MoreToLess, MoreToLessN, LessToMore, IQuizz
from .. import AF, GOODBAD, TIMESPAN, FREQUENCY, FREQUENCY1, FREQUENCY2, ASSESMENT
from ..interfaces import IQuizzSecurity
from uvclight.utils import current_principal
from collections import OrderedDict
from nva.psyquizz import Base
from grokcore.component import provides, context, global_utility, Subscription
from sqlalchemy import *
from zope import schema
from zope.location import Location
from zope.interface import implementer, Interface
from sqlalchemy.orm import relationship, backref


class IQuizz4(IQuizz2):
    pass


@implementer(IQuizz4)
class Quizz4(Base, Location):

    __tablename__ = 'quizz4'
    __schema__ = IQuizz4
    __title__ = u"Quizz4 test"
    __base_pdf__ = "kfza.pdf"

    id = Column('id', Integer, primary_key=True)

    # Link
    student_id = Column(String, ForeignKey('students.access'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    student = relationship("Student", backref="answer")

    # Quizz 2 base
    completion_date = Column('completion_date', DateTime)
    question1 = Column('question1', Integer)
    question2 = Column('question2', Integer)
    question3 = Column('question3', Integer)
    question4 = Column('question4', Integer)
    question5 = Column('question5', Integer)
    question6 = Column('question6', Integer)
    question7 = Column('question7', Integer)
    question8 = Column('question8', Integer)
    question9 = Column('question9', Integer)
    question10 = Column('question10', Integer)
    question11 = Column('question11', Integer)
    question12 = Column('question12', Integer)
    question13 = Column('question13', Integer)
    question14 = Column('question14', Integer)
    question15 = Column('question15', Integer)
    question16 = Column('question16', Integer)
    question17 = Column('question17', Integer)
    question18 = Column('question18', Integer)
    question19 = Column('question19', Integer)
    question20 = Column('question20', Integer)
    question21 = Column('question21', Integer)
    question22 = Column('question22', Integer)
    question23 = Column('question23', Integer)
    question24 = Column('question24', Integer)
    question25 = Column('question25', Integer)
    question26 = Column('question26', Integer)

    # Quizz3 Supplements
    should = Column('should', Text)

    # Extra questions
    extra_questions = Column('extra_questions', Text)


global_utility(Quizz4, provides=IQuizz, name='quizz4', direct=True)
