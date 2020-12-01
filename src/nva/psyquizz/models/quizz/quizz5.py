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

    question1 = Column("question1", Boolean)
    question2 = Column("question2", Boolean)
    question3 = Column("question3", Boolean)
    question4 = Column("question4", Boolean)
    question5 = Column("question5", Boolean)
    question6 = Column("question6", Boolean)
    question7 = Column("question7", Boolean)
    question8 = Column("question8", Boolean)
    question9 = Column("question9", Boolean)
    question10 = Column("question10", Boolean)
    question11 = Column("question11", Boolean)
    question12 = Column("question12", Boolean)
    question13 = Column("question13", Boolean)
    question14 = Column("question14", Boolean)
    question15 = Column("question15", Boolean)
    question16 = Column("question16", Boolean)
    question17 = Column("question17", Boolean)
    question18 = Column("question18", Boolean)
    question19 = Column("question19", Boolean)
    question20 = Column("question20", Boolean)
    question21 = Column("question21", Boolean)
    question22 = Column("question22", Boolean)
    question23 = Column("question23", Boolean)
    question24 = Column("question24", Boolean)
    question25 = Column("question25", Boolean)
    question26 = Column("question26", Boolean)
    question27 = Column("question27", Boolean)
    question28 = Column("question28", Boolean)
    question29 = Column("question29", Boolean)
    question30 = Column("question30", Boolean)
    question31 = Column("question31", Boolean)
    question32 = Column("question32", Boolean)
    question33 = Column("question33", Boolean)
    question34 = Column("question34", Boolean)
    question35 = Column("question35", Boolean)
    question36 = Column("question36", Boolean)
    question37 = Column("question37", Boolean)
    question38 = Column("question38", Boolean)
    question39 = Column("question39", Boolean)
    question40 = Column("question40", Boolean)
    question41 = Column("question41", Boolean)
    question42 = Column("question42", Boolean)
    question43 = Column("question43", Boolean)
    question44 = Column("question44", Boolean)
    question45 = Column("question45", Boolean)
    question46 = Column("question46", Boolean)
    question47 = Column("question47", Boolean)
    question48 = Column("question48", Boolean)
    question49 = Column("question49", Boolean)
    question50 = Column("question50", Boolean)
    question51 = Column("question51", Boolean)
    question52 = Column("question52", Boolean)
    question53 = Column("question53", Boolean)
    question54 = Column("question54", Boolean)
    question55 = Column("question55", Boolean)
    question56 = Column("question56", Boolean)
    question57 = Column("question57", Boolean)
    question58 = Column("question58", Boolean)
    question59 = Column("question59", Boolean)
    question60 = Column("question60", Boolean)
    question61 = Column("question61", Boolean)
    question62 = Column("question62", Boolean)
    question63 = Column("question63", Boolean)
    question64 = Column("question64", Boolean)
    question65 = Column("question65", Boolean)
    question66 = Column("question66", Boolean)
    question67 = Column("question67", Boolean)
    question68 = Column("question68", Boolean)
    question69 = Column("question69", Boolean)
    question70 = Column("question70", Boolean)
    question71 = Column("question71", Boolean)
    question72 = Column("question72", Boolean)

    extra_questions = Column("extra_questions", Text)


global_utility(Quizz5, provides=IQuizz, name="quizz5", direct=True)
