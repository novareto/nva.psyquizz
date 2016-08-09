# -*- coding: utf-8 -*-

import json

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


#@menuentry(IContextualActionsMenu, order=0)
class CriteriasListing(Page):
    name('index')
    title(_(u'Frontpage'))
    context(ICriterias)
    require('manage.company')
    order(0)

    template = get_template('criterias.pt', __file__)


#@menuentry(IContextualActionsMenu, order=0)
class CompanyHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Company)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('company.pt', __file__)


#@menuentry(IContextualActionsMenu, order=0)
class AccountHomepage(Page):
    name('display')
    title(_(u'Frontpage'))
    context(Account)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('account.pt', __file__)



@menuentry(IContextualActionsMenu, order=0)
class CompanyCourseHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Course)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('course.pt', __file__)

    def update(self):
        self.criterias = {
            c.title: [v.strip() for v in c.items.split('\n') if v.strip()]
            for c in self.context.criterias}

        voc = quizz_choice(self.context)
        self.quizz_name = voc.getTermByToken(self.context.quizz_type).title


@menuentry(IContextualActionsMenu, order=0)
class CompanySessionHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(ClassSession)
    require('manage.company')
    template = get_template('session.pt', __file__)


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
