# -*- coding: utf-8 -*-

import binascii
import base64
from datetime import date
from . import Site
from ..interfaces import IAnonymousRequest, QuizzAlreadyCompleted, QuizzClosed
from ..models import Student, Course, ClassSession
from cromlech.browser import IPublicationRoot
from dolmen.sqlcontainer import SQLContainer
from uvc.content.interfaces import IContent
from uvc.themes.btwidgets import IBootstrapRequest
from uvclight.backends.sql import SQLPublication
from zope.component import getGlobalSiteManager
from zope.interface import implementer


def get_id(secret):
    return int(base64.urlsafe_b64decode(binascii.unhexlify(secret)).split(' ', 1)[0])


@implementer(IContent, IPublicationRoot)
class QuizzBoard(SQLContainer):
    model = Student
    assert_key = 'completion_date'

    def getSiteManager(self):
        return getGlobalSiteManager()

    def __getitem__(self, id):
        if id.startswith('generic'):
            try:
                sessionid = get_id(str(id[8:]))
                session = self.session.query(ClassSession).get(sessionid)
                assert session is not None
                if date.today() > session.enddate:
                    raise QuizzClosed(self)
                uuid = self.model.generate_access()
                student = self.model(
                    access=uuid,
                    company_id=session.course.company_id,
                    session_id=sessionid,
                    course=session.course,
                    quizz_type=session.course.quizz_type)

                self.session.add(student)
                student.__name__ = uuid
                student.__parent__ = self
                return student
            except QuizzClosed:
                raise
            except:
                raise KeyError(id)
        else:
            content = SQLContainer.__getitem__(self, id)
            if date.today() > content.session.enddate:
                raise QuizzClosed(content)
            if getattr(content, 'completion_date') is not None:
                raise QuizzAlreadyCompleted(content)
            return content


class Application(SQLPublication):
    layers = [IBootstrapRequest, IAnonymousRequest]

    def setup_database(self, engine):
        pass

    def site_manager(self, environ):
        return Site(QuizzBoard(None, '', self.name))
