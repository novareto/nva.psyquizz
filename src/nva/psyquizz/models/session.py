# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from zope.interface import implementer
from zope.location import Location
from .interfaces import IClassSession
from .student import Student


@implementer(IClassSession)
class ClassSession(Base, Location):

    isEditable = True
    isDeletable = True

    __tablename__ = 'sessions'
    model = Student

    id = Column('id', Integer, primary_key=True)
    startdate = Column('startdate', Date)
    enddate = Column('enddate', Date)
    strategy = Column('strategy', String(20))
    p2p = Column('p2p', Boolean)
    company_id = Column(Integer, ForeignKey('companies.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    about = Column('about', Text)
    _students = relationship(
        "Student", backref="session",
        collection_class=attribute_mapped_collection('access'))

    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)

    def append(self, value):
        self._students[value.access] = value

    @property
    def title(self):
        mid = min([x.id for x in self.course.sessions])
        if self.id == mid:
            return "Erstbefragung"
        return "Wiederholungsbefragung (%s.%s)" %(self.startdate.strftime('%m'),
                self.startdate.strftime('%Y'))

    @property
    def students(self):
        for key, student in self._students.items():
            student.__parent__ = self
            yield student

    def __getitem__(self, key):
        student = self._students[key]
        student.__parent__ = self
        return student

    @property
    def __name__(self):
        return str(self.id)

    @property
    def quizz_type(self):
        return self.course.quizz_type

    def generate_students(self, nb):
        for i in xrange(0, nb):
            access = self.model.generate_access()
            yield self.model(
                access=access,
                company_id=self.company_id,
                course_id=self.course.id,
                quizz_type=self.course.quizz_type)

    @property
    def uncomplete(self):
        for key, student in self._students.items():
            student.__parent__ = self
            if student.completion_date is None:
                yield student

    @property
    def complete(self):
        for key, student in self._students.items():
            student.__parent__ = self
            if student.completion_date is not None:
                yield student

    @property
    def anon_complete(self):
        return [x for x in self.complete if x.anonymous == True]

    @property
    def strat_title(self):
        from nva.psyquizz.browser.forms import IPopulateCourse
        source = IPopulateCourse['strategy'].source(None)
        if not self.strategy:
            return "free"
        return source.getTermByToken(self.strategy).title


# standard decorator style
from sqlalchemy import event
from zope.component import queryUtility
from zope.interface import alsoProvides

@event.listens_for(ClassSession, 'load')
def receive_load(target, context):
    from nva.psyquizz.models.quizz.quizz2 import IQuizz
    util = queryUtility(IQuizz, target.quizz_type)
    if util is not None:
        alsoProvides(target, util.__schema__)
