# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from zope.interface import implementer
from .interfaces import ICriteria
from uvc.content.interfaces import IDescriptiveSchema


criterias_table = Table('criterias_courses', Base.metadata,
    Column('courses_id', Integer, ForeignKey('courses.id')),
    Column('criterias_id', Integer, ForeignKey('criterias.id')),
    Column('company_id', Integer, ForeignKey('companies.id')),
)


@implementer(ICriteria, IDescriptiveSchema)
class Criteria(Base):

    isEditable = True
    isDeletable = True

    __tablename__ = 'criterias'

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    items = Column('items', Text)
    company_id = Column(Integer, ForeignKey('companies.id'))

    @property
    def traversable_id(self):
        return str(self.id)



class CriteriaAnswer(Base):

    __tablename__ = 'criteria_answers'

    criteria_id = Column(Integer, ForeignKey('criterias.id'), primary_key=True)
    student_id = Column(String, ForeignKey('students.access'), primary_key=True)
    completion_date = Column('completion_date', DateTime,
                             default=datetime.utcnow)
    answer = Column('answer', String)

    criteria = relationship("Criteria",
                            backref=backref("answers", cascade="all,delete"))
    student = relationship("Student",
                           backref=backref("criterias", cascade="all,delete"))
