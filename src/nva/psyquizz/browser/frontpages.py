# -*- coding: utf-8 -*-

import json
import base64
import datetime
import binascii

from collections import OrderedDict
from cromlech.browser import exceptions
from cromlech.sqlalchemy import get_session
from dolmen.menu import menuentry, order
from nva.psyquizz.extra_questions import parse_extra_question_syntax
from uvc.design.canvas import IContextualActionsMenu
from uvclight import layer, name, context, title, get_template
from uvclight.auth import require
from zope.component import getUtility
from zope.schema import getFieldsInOrder

from . import Page
from .differences import sessions, have_courses_to_compare
from .. import quizzjs
from ..apps import anonymous
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..models import Account, Company, Course, ClassSession
from ..models import IQuizz, ICriterias
from ..models.deferred import quizz_choice_full



TEXT = u"""
Auf Grund massiver technischer Störungen waren wir gezwungen, eine Datensicherung mit Stand Sonntag 24.03. einzuspielen. Das bedeutet, dass „Fragebögen“ die zwischen Montag 25.03. und Mittwoch 27.03. eingegeben wurden leider verloren gegangen sind. Wir möchten Sie bitten dies zu entschuldigen.

Bei Rückfragen wenden Sie sich bitte an gbpb@bgetem.de oder 0221-3778-6207
"""


class AccountHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Account)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('frontpage.pt', __file__)

    maxResults = 7 

    def update(self):
        #self.flash(TEXT)
        quizzjs.need()

    def canCompare(self, company):
        courses = have_courses_to_compare(company)
        return courses

    def canDiff(self, course):
        if course.__parent__.quizz_type not in ('quizz2', 'quizz5'):
            return False
        courses = len(list(course))
        if courses > 1:
            if len(sessions(course.__parent__, threshold=7)) > 1:
                return True
        return False

    def canRepeatQuestionaire(self, course):
        ret = False
        for session in course.sessions:
            if self.checkDate(session.enddate):
                ret = True
        return ret

    def quizz_name(self, course):
        voc = quizz_choice_full(course)
        try:
            return voc.getTermByToken(course.quizz_type).title
        except LookupError:
            return 'Unavailable quizz type'

    def generic_id(self, id):
        return binascii.hexlify(
            base64.urlsafe_b64encode(str(id) + ' complexificator'))

    def checkDate(self, date):
        now = datetime.datetime.now()
        if date < now.date():
            return True
        return False

    def additional_questions(self, course):
        ret = {'title': '', 'content': [], 'show': False}
        if not course.extra_questions:
            ret['title'] = u'Keine Frage angelegt'
        else:
            ret['show'] = True
            exq = course.extra_questions.strip().split('\n')
            ret['title'] = u'%s Frage(n) angelegt' % len(exq)
            for l, tp, opts in (parse_extra_question_syntax(e) for e in exq):
                ret['content'].append(l)
        return ret


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
    context(IQuizz)
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
