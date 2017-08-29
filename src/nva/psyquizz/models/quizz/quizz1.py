# -*- coding: utf-8 -*-

from .. import TrueOrFalse, IQuizz

from collections import OrderedDict
from nva.psyquizz import Base
from sqlalchemy import *
from grokcore.component import global_utility
from zope.interface import Interface, implementer
from zope.location import Location
from zope import schema
from sqlalchemy.orm import relationship, backref


class IGroup1(Interface):

    question1 = schema.Choice(
        title=u"1",
        description=u"Wird die auszuführende Arbeit von Ihnen selbst vorbereitet, organisiert und geprüft?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question2 = schema.Choice(
        title=u"2",
        description=u"Ist Ihre Tätigkeit abwechslungsreich?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question3 = schema.Choice(
        title=u"3",
        description=u"Haben Sie die Möglichkeit, eine wechselnde Körperhaltung einzunehmen?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question4 = schema.Choice(
        title=u"4",
        description=u"Erhalten Sie ausreichende Informationen zum eigenen Arbeitsbereich?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question5 = schema.Choice(
        title=u"5",
        description=u"Entspricht Ihre Qualifikation den Anforderungen, die durch die Tätigkeit gestellt werden?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question6 = schema.Choice(
        title=u"6",
        description=u"Ist die Tätigkeit frei von erhöhter Verletzungs- und Erkrankungsgefahr?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question7 = schema.Choice(
        title=u"7",
        description=u"Ist Ihre Tätigkeit frei von ungünstigen Arbeitsumgebungsbedingungen (z. B. Lärm, Klima, Gerüche)?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question8 = schema.Choice(
        title=u"8",
        description=u"Ist Ihre Tätigkeit frei von erhöhten emotionalen Anforderungen (z. B. im Publikumsverkehr)?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question9 = schema.Choice(
        title=u"9",
        description=u"Haben Sie Einfluss auf die Zeiteinteilung Ihrer Arbeit (z. B. Lage der Pausen, Arbeitstempo, Termine)?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question10 = schema.Choice(
        title=u"10",
        description=u"Haben Sie Einfluss auf die Vorgehensweise bei Ihrer Arbeit (z. B. Wahl der Arbeitsmittel/-methoden)?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question11 = schema.Choice(
        title=u"11",
        description=u"ErhaltenSieausreichendeInformationenzurEntwicklungdesBetriebes?",
        vocabulary=TrueOrFalse,
        required=True,
        )


class IGroup2(Interface):

    question12 = schema.Choice(
        title=u"12",
        description=u"Ist ein kontinuierliches Arbeiten ohne häufige Störungen möglich?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question13 = schema.Choice(
        title=u"13",
        description=u"Können Sie überwiegend ohne Zeit -und Termindruck arbeiten?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question14 = schema.Choice(
        title=u"14",
        description=u"Erhalten Sie ausreichende Rückmeldung (Anerkennung, Kritik, Beurteilung) über die eigene Leistung?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question15 = schema.Choice(
        title=u"15",
        description=u"Gibt es für Sie klare Entscheidungsstrukturen?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question16 = schema.Choice(
        title=u"16",
        description=u"Sind angeordnete Überstunden die Ausnahme?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question17 = schema.Choice(
        title=u"17",
        description=u"Wird Ihnen im Falle von Überstunden zeitnah Freizeitausgleich gewährt?",
        vocabulary=TrueOrFalse,
        required=True,
        )


class IGroup3(Interface):

    question18 = schema.Choice(
        title=u"18",
        description=u"Bietet Ihre Tätigkeit die Möglichkeit zur Zusammenarbeit mit Kolleginnen / Kollegen?",
        vocabulary=TrueOrFalse,
        required=True,
        )

    question19 = schema.Choice(
        title=u"19",
        description=u"Besteht ein positives soziales Klima?",
        vocabulary=TrueOrFalse,
        required=True,
        )


IGroup1.setTaggedValue('label', u'Fragen zur Tätigkeit')
IGroup2.setTaggedValue('label', u'Fragen zur Arbeitsorganisation')
IGroup3.setTaggedValue('label', u'Fragen zum sozialen Umfeld')


class IQuizz1(IQuizz, IGroup1, IGroup2, IGroup3):
    pass


IQuizz1.setTaggedValue(
    'averages', OrderedDict((
        (u'Tätigkeit', map(str, range(1, 12))),
        (u'Arbeitsorganisation', map(str, range(12, 18))),
        (u'Sozialen Umfeld', map(str, range(18, 20))),
    )))


@implementer(IQuizz1)
class Quizz1(Base, Location):

    __tablename__ = 'quizz1'
    __schema__ = IQuizz1
    __title__ = u"Prüfliste Psychische Belastung"
    __base_pdf__ = "kfza.pdf"

    id = Column('id', Integer, primary_key=True)

    # Link
    student_id = Column(String, ForeignKey('students.access'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))

    student = relationship("Student")

    # Quizz
    completion_date = Column('completion_date', DateTime)
    question1 = Column('question1', Boolean)
    question2 = Column('question2', Boolean)
    question3 = Column('question3', Boolean)
    question4 = Column('question4', Boolean)
    question5 = Column('question5', Boolean)
    question6 = Column('question6', Boolean)
    question7 = Column('question7', Boolean)
    question8 = Column('question8', Boolean)
    question9 = Column('question9', Boolean)
    question10 = Column('question10', Boolean)
    question11 = Column('question11', Boolean)
    question12 = Column('question12', Boolean)
    question13 = Column('question13', Boolean)
    question14 = Column('question14', Boolean)
    question15 = Column('question15', Boolean)
    question16 = Column('question16', Boolean)
    question17 = Column('question17', Boolean)
    question18 = Column('question18', Boolean)
    question19 = Column('question19', Boolean)
    extra_questions = Column('extra_questions', Text)


global_utility(Quizz1, provides=IQuizz, name='quizz1', direct=True)
