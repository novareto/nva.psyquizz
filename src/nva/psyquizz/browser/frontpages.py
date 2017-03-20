# -*- coding: utf-8 -*-

import json
import base64
import datetime
import binascii

from ..apps import anonymous
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..models import Account, Company, Student, Course, ClassSession
from ..models import IQuizz, ICriterias
from ..models.deferred import quizz_choice
from collections import OrderedDict
from cromlech.browser import exceptions
from cromlech.sqlalchemy import get_session
from dolmen.menu import menuentry, order
from uvc.design.canvas import IContextualActionsMenu
from uvclight import Page
from uvclight import layer, name, context, title, get_template
from uvclight.auth import require
from zope.component import getUtility
from zope.schema import getFieldsInOrder
from .. import quizzjs


class AccountHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Account)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('ckh.pt', __file__)

    maxResults = 1

    def update(self):
        quizzjs.need()

    def quizz_name(self, course):
        voc = quizz_choice(course)
        return voc.getTermByToken(course.quizz_type).title

    def generic_id(self, id):
        return binascii.hexlify(base64.urlsafe_b64encode(str(id) + ' complexificator'))

    def checkDate(self, date):
        now = datetime.datetime.now()
        if date < now.date():
            return True
        return False


class CriteriasListing(Page):
    name('index')
    title(_(u'Frontpage'))
    context(ICriterias)
    require('manage.company')
    order(0)

    template = get_template('criterias.pt', __file__)


class CompanyHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Company)
    layer(ICompanyRequest)
    require('manage.company')

    def render(self):
        self.redirect(self.application_url())
        return "" 


@menuentry(IContextualActionsMenu, order=0)
class CompanyCourseHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Course)
    layer(ICompanyRequest)
    require('manage.company')

    def render(self):
        self.redirect(self.application_url())
        return "" 


@menuentry(IContextualActionsMenu, order=0)
class CompanySessionHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(ClassSession)
    require('manage.company')

    def render(self):
        self.redirect(self.application_url())
        return "" 


class StudentHomepage(Page):
    name('index')
    context(Student)
    require('zope.Public')

    template = get_template('student.pt', __file__)

    def update(self):
        session = get_session('school')
        quizz = getUtility(IQuizz, name=self.context.quizz_type)
        answers = list(session.query(quizz).filter(
            quizz.student_id == self.context.access))
        if len(answers) == 1:
            self.answers = answers[0]
            self.fields = OrderedDict(getFieldsInOrder(quizz.__schema__))
            self.extra = json.loads(self.answers.extra_questions)


class QuizzHomepage(Page):
    name('index')
    context(anonymous.QuizzBoard)
    require('zope.Public')

    def __call__(self):
        raise exceptions.HTTPForbidden(self.context)
