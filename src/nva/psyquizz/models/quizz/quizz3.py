# -*- coding: utf-8 -*-


from .quizz2 import Quizz2, IQuizz2
from .. import MoreToLess, MoreToLessN, LessToMore, IQuizz
from .. import AF, GOODBAD, TIMESPAN, FREQUENCY, FREQUENCY1, FREQUENCY2, ASSESMENT

from collections import OrderedDict
from nva.psyquizz import Base
from grokcore.component import global_utility
from sqlalchemy import *
from zope import schema
from zope.location import Location
from zope.interface import implementer
from sqlalchemy.orm import relationship, backref


### VOCABULARIES NEED FIXING

class IQuizz3(IQuizz2):

    question27 = schema.Choice(
        title=u"27",
        description=u"<blockquote> Frageteil:  Work Ability Index </blockquote> Wenn Sie Ihre beste, je erreichte Arbeitsfähigkeit mit 10 Punkten bewerten:<br/> Wie viele Punkte würden Sie dann für Ihre derzeitige Arbeitsfähigkeit geben? (0 bedeutet, dass Sie derzeit arbeitsunfähig sind)",
        vocabulary=AF,
        required=True,
        )

    question28 = schema.Choice(
        title=u"28",
        description=u"Wie schätzen Sie Ihre derzeitige Arbeitsfähigkeit in Bezug auf die <u>körperlichen</u> Arbeitsanforderungen ein?",
        vocabulary=GOODBAD,
        required=True,
        )

    question29 = schema.Choice(
        title=u"29",
        description=u"Wie schätzen Sie Ihre derzeitige Arbeitsfähigkeit in Bezug auf die <u>psychischen</u> Arbeitsanforderungen ein?",
        vocabulary=GOODBAD,
        required=True,
        )

    question30 = schema.Choice(
        title=u"30",
        description=u"Wie viele ganze Tage blieben Sie auf Grund eines gesundheitlichen Problems (Krankheit, Gesundheitsvorsorge oder Untersuchung) im letzten Jahr (12 Monate) der Arbeit fern?",
        vocabulary=TIMESPAN,
        required=True,
        )

    question31 = schema.Choice(
        title=u"31",
        description=u"Glauben Sie, dass Sie, ausgehend von Ihrem jetzigen Gesundheitszustand, Ihre derzeitige Arbeit auch in den nächsten zwei Jahren ausüben können?",
        vocabulary=ASSESMENT,
        required=True,
        )

    question32 = schema.Choice(
        title=u"32",
        description=u"Haben Sie in der letzten Zeit Ihre täglichen Aufgaben mit Freude erledigt?",
        vocabulary=FREQUENCY,
        required=True,
        )

    question33 = schema.Choice(
        title=u"33",
        description=u"Waren Sie in letzter Zeit aktiv und rege?",
        vocabulary=FREQUENCY1,
        required=True,
        )

    question34 = schema.Choice(
        title=u"34",
        description=u"Waren Sie in der letzten Zeit zuversichtlich, was die Zukunft betrifft?",
        vocabulary=FREQUENCY2,
        required=True,
        )


for tag in IQuizz2.getTaggedValueTags():
    IQuizz3.setTaggedValue(
        tag, IQuizz2.getTaggedValue(tag),
    )

IQuizz3.setTaggedValue(
    'sums', OrderedDict((
        ('27', ('27',)),
        ('28', ('28',)),
        ('29', ('29',)),
        ('30', ('30',)),
        ('31', ('31',)),
        (u'Psychische Leistungsreserven', ('32', '33', '34')),
        )))



@implementer(IQuizz3)
class Quizz3(Base, Location):

    __tablename__ = 'quizz3'
    __schema__ = IQuizz3
    __title__ = u"KFZA Kurzfragebogen zur Arbeitsanalyse + WAI Fragebogen"
    __base_pdf__ = ""

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
    question27 = Column('question27', Integer)
    question28 = Column('question28', Integer)
    question29 = Column('question29', Integer)
    question30 = Column('question30', Integer)
    question31 = Column('question31', Integer)
    question32 = Column('question32', Integer)
    question33 = Column('question33', Integer)
    question34 = Column('question34', Integer)

    # Extra questions
    extra_questions = Column('extra_questions', Text)


global_utility(Quizz3, provides=IQuizz, name='quizz3', direct=True)
