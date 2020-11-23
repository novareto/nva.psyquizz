# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from nva.psyquizz.models import TrueOrFalse, IQuizz
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
        description=u"Wird die auszuführende Arbeit von Ihnen selbst vorbereitet, organisiert und geprüft?",
        vocabulary=TrueOrFalse,
        required=True,
    )


class IScale2(Interface):

    question2 = schema.Choice(
        title=u"2",
        description=u"Ist ein kontinuierliches Arbeiten ohne häufige Störungen möglich?",
        vocabulary=TrueOrFalse,
        required=True,
    )


IScale1.setTaggedValue("label", u"Fragen zur Tätigkeit")
IScale2.setTaggedValue("label", u"Fragen zur Arbeitsorganisation")


class IQuizz5(IQuizz, IScale1, IScale2):
    pass


IQuizz5.setTaggedValue(
    "averages", OrderedDict(((u"Tätigkeit", map(str, range(1, 12))),))
)


IQuizz5.setTaggedValue(
    "descriptions",
    {
        "1": u" Selbst organisiertes Arbeiten",
        "2": u" Abwechslungsreichtum",
    },
)


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
    extra_questions = Column("extra_questions", Text)


global_utility(Quizz5, provides=IQuizz, name="quizz5", direct=True)
