# -*- coding: utf-8 -*-

import binascii
import base64
from datetime import date
from . import Site
from ..interfaces import IAnonymousRequest, QuizzAlreadyCompleted, QuizzClosed
from ..models import Student, ClassSession
from cromlech.browser import IPublicationRoot
from dolmen.sqlcontainer import SQLContainer
from uvc.content.interfaces import IContent
from uvc.themes.btwidgets import IBootstrapRequest
from uvclight.backends.sql import SQLPublication
from zope.component import getGlobalSiteManager
from zope.interface import implementer
from cromlech.sqlalchemy import get_session
from zope.location import ILocation, LocationProxy, locate
from nva.psyquizz.models.student import student_quizz


def get_id(secret):
    return int(
        base64.urlsafe_b64decode(binascii.unhexlify(secret)).split(' ', 1)[0])


@implementer(IContent, IPublicationRoot)
class QuizzBoard(SQLContainer):
    model = Student
    assert_key = 'completion_date'
    db_key = "school"

    #def __init__(self, configuration, parent=None):
    #    self.__parent__ = parent
    #    self.__name__ = configuration.name
    #    self.configuration = configuration

    def getSiteManager(self):
        return getGlobalSiteManager()

    def key_converter(self, id):
        return id

    def create_student(self, id):
        sessionid = get_id(str(id))
        session = self.session.query(ClassSession).get(sessionid)
        assert session is not None
        if date.today() > session.enddate:
            raise QuizzClosed(self)
        uuid = self.model.generate_access()
        student = self.model(
            anonymous=True,
            access=uuid,
            company_id=session.course.company_id,
            session_id=sessionid,
            course=session.course,
            quizz_type=session.course.quizz_type)

        self.session.add(student)
        student.__name__ = uuid
        student.__parent__ = self
        student_quizz(student, None)
        return student

    def __contains__(self, id):
        try:
            key = self.key_converter(id)
        except ValueError:
            return False
        model = self.session.query(self.model).get(key)
        if model is None:
            return False
        return True

    def get(self, id, default=None):
        if not id.startswith('generic'):
            try:
                content = self.__getitem__(id)
                return content
            except KeyError:
                return default
        return None

    def __getitem__(self, id):
        if id.startswith('generic'):
            try:
                return self.create_student(str(id[8:]))
            except QuizzClosed:
                raise
            except:
                raise KeyError(id)
        else:
            content = self.getStudent(id)
            if content is not None:
                if date.today() > content.session.enddate:
                    raise QuizzClosed(content)
                if getattr(content, 'completion_date') is not None:
                    raise QuizzAlreadyCompleted(content)
                return content
            raise KeyError(id)

    def getStudent(self, key):
        model = self.query_filters(self.session.query(self.model)).get(key)
        if model is None:
            raise KeyError(key)

        if not ILocation.providedBy(model):
            model = LocationProxy(model)

        locate(model, self, self.key_reverse(model))
        student_quizz(model, None)
        return model


def get_my_session():
    return get_session('school')


class Application(SQLPublication):
    _layers = [IBootstrapRequest, IAnonymousRequest]

    def setup_database(self, engine):
        pass

    def site_manager(self, environ):
        #return Site(QuizzBoard(self.configuration, parent=None))
        return Site(QuizzBoard(get_my_session, name=self.configuration.name, parent=None))

    @property
    def layers(self):
        if self.configuration.layer is not None:
            return [self.configuration.layer] + self._layers
        return self._layers
