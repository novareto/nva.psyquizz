# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from nva.psyquizz.models import FBGU, IQuizz
from nva.psyquizz.models.quizz import QuizzBase

from collections import OrderedDict
from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, Text
from grokcore.component import global_utility
from zope.interface import Interface, implementer
from zope import schema
from sqlalchemy.orm import relationship, backref


class IScale1(Interface):

    question1 = schema.Choice(
        title=u"1",
        description=u"Bei der Arbeit bin ich an Arbeitsvorgängen von Anfang bis Ende beteiligt.",
        vocabulary=FBGU,
        required=True,
    )

    question2 = schema.Choice(
        title=u"2",
        description=u"Bei meiner Arbeit führt man nicht nur kleine Teilaufgaben aus, sondern stellt vollständige Produkte und Dienstleistungen her.",
        vocabulary=FBGU,
        required=True,
    )

    question3 = schema.Choice(
        title=u"3",
        description=u"Ich muss vorgegebene Arbeiten nicht nur ausführen, sondern auch selbst planen und die Ergebnisse überprüfen.",
        vocabulary=FBGU,
        required=True,
    )


class IScale2(Interface):

    question4 = schema.Choice(
        title=u"4",
        description=u"Bei meiner Arbeit kann man die Reihenfolge der Aufgabenerledigung selbst bestimmen.",
        vocabulary=FBGU,
        required=True,
    )

    question5 = schema.Choice(
        title=u"5",
        description=u"Man kann bei meiner Arbeit selbst bestimmen, wann man was macht.",
        vocabulary=FBGU,
        required=True,
    )

    question6 = schema.Choice(
        title=u"6",
        description=u"Man hat viele Freiheiten in der Art und Weise, wie man seine Arbeit verrichtet.",
        vocabulary=FBGU,
        required=True,
    )


class IScale3(Interface):

    question7 = schema.Choice(
        title=u"7",
        description=u"Bei meiner Arbeit hat man fast jeden Tag etwas anderes zu tun.",
        vocabulary=FBGU,
        required=True,
    )

    question8 = schema.Choice(
        title=u"8",
        description=u"Die Arbeitsaufgaben wechseln häufig bei meiner Arbeit.",
        vocabulary=FBGU,
        required=True,
    )

    question9 = schema.Choice(
        title=u"9",
        description=u"Man muss bei meiner Arbeit unterschiedliche Fähigkeiten einsetzen.",
        vocabulary=FBGU,
        required=True,
    )


class IScale4(Interface):

    question10 = schema.Choice(
        title=u"10",
        description=u"Man muss viel Energie dafür aufwenden, die für die Arbeit notwendigen Informationen zu beschaffen.",
        vocabulary=FBGU,
        required=True,
    )

    question11 = schema.Choice(
        title=u"11",
        description=u"Erforderliche Unterlagen, Informationen und Daten sind häufig unvollständig.",
        vocabulary=FBGU,
        required=True,
    )

    question12 = schema.Choice(
        title=u"12",
        description=u"Entscheidungen werden erschwert, weil häufig nicht alle notwendigen Informationen vorliegen.",
        vocabulary=FBGU,
        required=True,
    )


class IQuizz5(IQuizz, IScale1, IScale2, IScale3, IScale4):
    pass


IQuizz5.setTaggedValue("scales", [
    {'iface': IScale1, 'label': u"Vollständigkeit der Aufgabe"},
    {'iface': IScale2, 'label': u"Handlungsspielraum"},
    {'iface': IScale3, 'label': u"Variabilität"},
    {'iface': IScale4, 'label': u"Informationsmängel"},
])


IQuizz5.setTaggedValue("averages", OrderedDict((
    (u'Vollständigkeit der Aufgabe', [x[1].title for x in schema.getFieldsInOrder(IScale1)]),
    (u'Handlungsspielraum', [x[1].title for x in schema.getFieldsInOrder(IScale2)]),
    (u'Some random name', [x[1].title for x in schema.getFieldsInOrder(IScale3)]),
    (u'Other randomish name', [x[1].title for x in schema.getFieldsInOrder(IScale4)])
    )))


@implementer(IQuizz5)
class Quizz5(QuizzBase, Base):

    __tablename__ = "quizz5"
    __schema__ = IQuizz5
    __title__ = u"FBGU Fragebogen"
    __base_pdf__ = "fbgu.pdf"
    __supports_diff__ = False

    __table_args__ = {"extend_existing": True}

    id = Column("id", Integer, primary_key=True)

    # Link
    student_id = Column(String, ForeignKey("students.access"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))

    student = relationship(
        "Student",
        cascade="all,delete",
        backref=backref(
            "quizz5", uselist=False, cascade="save-update,delete", single_parent=True
        ),
    )

    # Quizz
    completion_date = Column("completion_date", DateTime)

    question1 = Column("question1", Integer)
    question2 = Column("question2", Integer)
    question3 = Column("question3", Integer)
    question4 = Column("question4", Integer)
    question5 = Column("question5", Integer)
    question6 = Column("question6", Integer)
    question7 = Column("question7", Integer)
    question8 = Column("question8", Integer)
    question9 = Column("question9", Integer)
    question10 = Column("question10", Integer)
    question11 = Column("question11", Integer)
    question12 = Column("question12", Integer)
    question13 = Column("question13", Integer)
    question14 = Column("question14", Integer)
    question15 = Column("question15", Integer)
    question16 = Column("question16", Integer)
    question17 = Column("question17", Integer)
    question18 = Column("question18", Integer)
    question19 = Column("question19", Integer)
    question20 = Column("question20", Integer)
    question21 = Column("question21", Integer)
    question22 = Column("question22", Integer)
    question23 = Column("question23", Integer)
    question24 = Column("question24", Integer)
    question25 = Column("question25", Integer)
    question26 = Column("question26", Integer)
    question27 = Column("question27", Integer)
    question28 = Column("question28", Integer)
    question29 = Column("question29", Integer)
    question30 = Column("question30", Integer)
    question31 = Column("question31", Integer)
    question32 = Column("question32", Integer)
    question33 = Column("question33", Integer)
    question34 = Column("question34", Integer)
    question35 = Column("question35", Integer)
    question36 = Column("question36", Integer)
    question37 = Column("question37", Integer)
    question38 = Column("question38", Integer)
    question39 = Column("question39", Integer)
    question40 = Column("question40", Integer)
    question41 = Column("question41", Integer)
    question42 = Column("question42", Integer)
    question43 = Column("question43", Integer)
    question44 = Column("question44", Integer)
    question45 = Column("question45", Integer)
    question46 = Column("question46", Integer)
    question47 = Column("question47", Integer)
    question48 = Column("question48", Integer)
    question49 = Column("question49", Integer)
    question50 = Column("question50", Integer)
    question51 = Column("question51", Integer)
    question52 = Column("question52", Integer)
    question53 = Column("question53", Integer)
    question54 = Column("question54", Integer)
    question55 = Column("question55", Integer)
    question56 = Column("question56", Integer)
    question57 = Column("question57", Integer)
    question58 = Column("question58", Integer)
    question59 = Column("question59", Integer)
    question60 = Column("question60", Integer)
    question61 = Column("question61", Integer)
    question62 = Column("question62", Integer)
    question63 = Column("question63", Integer)
    question64 = Column("question64", Integer)
    question65 = Column("question65", Integer)
    question66 = Column("question66", Integer)
    question67 = Column("question67", Integer)
    question68 = Column("question68", Integer)
    question69 = Column("question69", Integer)
    question70 = Column("question70", Integer)
    question71 = Column("question71", Integer)
    question72 = Column("question72", Integer)

    extra_questions = Column("extra_questions", Text)


global_utility(Quizz5, provides=IQuizz, name="quizz5", direct=True)
