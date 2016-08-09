# -*- coding: utf-8 -*-

from .. import MoreToLess, MoreToLessN, LessToMore, IQuizz

from nva.psyquizz import Base
from nva.psyquizz.stats import ChartedQuizzStats
from grokcore.component import global_utility
from sqlalchemy import *
from zope import schema
from zope.interface import Interface, implementer
from zope.location import Location
from sqlalchemy.orm import relationship, backref


class IQuizz2(Interface):

    question1 = schema.Choice(
        title=u"1",
        description=u"Können Sie bei Ihrer Arbeit Neues dazulernen?",
        vocabulary=LessToMore,
        required=True,
        )

    question2 = schema.Choice(
        title=u"2",
        description=u"Können Sie bei Ihrer Arbeit Ihr Wissen und Können voll einsetzen?",
        vocabulary=LessToMore,
        required=True,
        )

    question3 = schema.Choice(
        title=u"3",
        description=u"Bei meiner Arbeit habe ich insgesamt gesehen häufig wechselnde, unterschiedliche Arbeitsaufgaben.",
        vocabulary=MoreToLess,
        required=True,
        )

    question4 = schema.Choice(
        title=u"4",
        description=u"Bei meiner Arbeit sehe ich selber am Ergebnis ob meine Arbeit, gut war oder nicht.",
        vocabulary=MoreToLess,
        required=True,
        )

    question5 = schema.Choice(
        title=u"5",
        description=u"Meine Arbeit ist so gestaltet, dass ich die Möglichkeit habe, ein vollständiges Arbeitsprodukt/eine vollständige Arbeitsaufgabe von Anfang bis Ende herzustellen.",
        vocabulary=MoreToLess,
        required=True,
        )

    question6 = schema.Choice(
        title=u"6",
        description=u"Bei dieser Arbeit gibt es Sachen, die zu kompliziert sind (z.B. aufgrund keiner oder unklarer Arbeitsbeschreibungen oder aufgrund mangelnder Qualifizierung).",
        vocabulary=MoreToLessN,
        required=True,
        )

    question7 = schema.Choice(
        title=u"7",
        description=u"Es werden zu hohe Anforderungen an meine Konzentrationsfähigkeit gestellt.",
        vocabulary=MoreToLessN,
        required=True,
        )

    question8 = schema.Choice(
        title=u"8",
        description=u"Ich stehe häufig unter Zeitdruck.",
        vocabulary=MoreToLessN,
        required=True,
        )

    question9 = schema.Choice(
        title=u"9",
        description=u"Ich habe zu viel Arbeit.",
        vocabulary=MoreToLessN,
        required=True,
        )

    question10 = schema.Choice(
        title=u"10",
        description=u"Oft stehen mir die benötigten Informationen, Materialien und Arbeitsmittel nicht zur Verfügung.",
        vocabulary=MoreToLessN,
        required=True,
        )

    question11 = schema.Choice(
        title=u"11",
        description=u"Ich werde bei meiner eigentlichen Arbeit immer wieder durch andere Personen unterbrochen.",
        vocabulary=MoreToLessN,
        required=True,
        )

    question12 = schema.Choice(
        title=u"12",
        description=u"An meinem Arbeitsplatz gibt es ungünstige Umgebungsbedingungen wie Lärm, Klima, Staub.",
        vocabulary=MoreToLessN,
        required=True,
        )

    question13 = schema.Choice(
        title=u"13",
        description=u"An meinem Arbeitsplatz sind Räume und Raumausstattung ungenügend",
        vocabulary=MoreToLessN,
        required=True,
        )
    
    question14 = schema.Choice(
        title=u"14",
        description=u"Wenn Sie Ihre Tätigkeit insgesamt betrachten, inwieweit können Sie die Reihenfolge der Arbeitsschritte selbst bestimmen?",
        vocabulary=LessToMore,
        required=True,
        )

    question15 = schema.Choice(
        title=u"15",
        description=u"Wie viel Einfluss haben Sie darauf, welche Arbeit Ihnen zugeteilt wird?",
        vocabulary=LessToMore,
        required=True,
        )

    question16 = schema.Choice(
        title=u"16",
        description=u"Können Sie Ihre Arbeit selbstständig planen und einteilen?",
        vocabulary=LessToMore,
        required=True,
        )

    question17 = schema.Choice(
        title=u"17",
        description=u"Ich kann mich auf Kollegen und Kolleginnen verlassen, wenn es bei der Arbeit schwierig wird.",
        vocabulary=MoreToLess,
        required=True,
        )

    question18 = schema.Choice(
        title=u"18",
        description=u"Ich kann mich auf meine/n direkte/n Vorgesetzte/n verlassen, wenn es bei der Arbeit schwierig wird.",
        vocabulary=MoreToLess,
        required=True,
        )

    question19 = schema.Choice(
        title=u"19",
        description=u"Man hält in der Abteilung gut zusammen.",
        vocabulary=MoreToLess,
        required=True,
        )

    question20 = schema.Choice(
        title=u"20",
        description=u"Diese Arbeit erfordert enge Zusammenarbeit mit anderen Kolleginnen und Kollegen in der Organisation.",
        vocabulary=MoreToLess,
        required=True,
        )

    question21 = schema.Choice(
        title=u"21",
        description=u"Ich kann mich während der Arbeit mit verschiedenen Kolleginnen und Kollegen über dienstliche und private Dinge unterhalten.",
        vocabulary=MoreToLess,
        required=True,
        )

    question22 = schema.Choice(
        title=u"22",
        description=u"Ich bekomme von Vorgesetzten und Kollegen immer Rückmeldung über die Qualität meiner Arbeit.",
        vocabulary=MoreToLess,
        required=True,
        )

    question23 = schema.Choice(
        title=u"23",
        description=u"Über wichtige Dinge und Vorgänge in unserer Organisation sind wir ausreichend informiert.",
        vocabulary=MoreToLess,
        required=True,
        )

    question24 = schema.Choice(
        title=u"24",
        description=u"Die Leitung unserer Organisation ist bereit, die Ideen und Vorschläge der Beschäftigten zu berücksichtigen.",
        vocabulary=MoreToLess,
        required=True,
        )

    question25 = schema.Choice(
        title=u"25",
        description=u"Unser Unternehmen bietet gute Weiterbildungsmöglichkeiten.",
        vocabulary=MoreToLess,
        required=True,
        )

    question26 = schema.Choice(
        title=u"26",
        description=u"Bei uns gibt es gute Aufstiegschancen (z.B. auch durch Erweiterung des bisherigen Tätigkeitsfeldes).",
        vocabulary=MoreToLess,
        required=True,
        )


@implementer(IQuizz2)
class Quizz2(Base, Location):

    __tablename__ = 'quizz2'
    __schema__ = IQuizz2
    __stats__ = ChartedQuizzStats
    __title__ = u"KFZA Kurzfragebogen zur Arbeitsanalyse"

    id = Column('id', Integer, primary_key=True)

    # Link
    student_id = Column(String, ForeignKey('students.access'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))

    student = relationship("Student")

    # Quizz
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
    extra_questions = Column('extra_questions', Text)


global_utility(Quizz2, provides=IQuizz, name='quizz2', direct=True)
