# -*- coding: utf-8 -*-

import json
import uvclight

from random import *
from zope.interface import Interface
from .results import Results
from .forms import ClassStats, CourseStats, CourseDiff
from ..apps import anonymous
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..interfaces import IQuizzLayer
from ..interfaces import QuizzAlreadyCompleted, QuizzClosed
from ..models import IQuizz, TrueOrFalse, IClassSession
from ..models import Company, Course, Student, CriteriaAnswer

from collections import OrderedDict
from cromlech.browser import IPublicationRoot
from cromlech.sqlalchemy import get_session
from dolmen.breadcrumbs.renderer import BreadcrumbsRenderer
from dolmen.menu import menuentry
from dolmen.message import receive
from dolmen.template import ITemplate
from grokcore.component import adapter, implementer
from nva.psyquizz import quizzjs, quizzcss
from siguvtheme.uvclight.viewlets import PersonalMenuViewlet
from sqlalchemy import or_, and_
from uvc.content import IDescriptiveSchema
from uvc.design.canvas import IFooter, IAboveContent, IBelowContent
from uvc.design.canvas import IContextualActionsMenu
from uvc.design.canvas import menus
from uvc.design.canvas.menus import INavigationMenu
from uvclight import Page, View, MenuItem
from uvclight import layer, title, name, menu, context, get_template
from uvclight.auth import require
from zope.component import getUtilitiesFor, getUtility
from zope.schema import getFieldsInOrder
from uvc.entities.browser.managers import IHeaders


def resolve_name(item):
    name = getattr(item, '__name__', None)
    if name is None and not IPublicationRoot.providedBy(item):
        raise KeyError('Object name (%r) could not be resolved.' % item)
    dc = IDescriptiveSchema(item, None)
    if dc is not None:
        return name, dc.title
    return name, name


class ResultsExtra(uvclight.ViewletManager):
    uvclight.order(10)
    uvclight.name('results_extra')


class Crumbs(BreadcrumbsRenderer, uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(10)
    uvclight.name('crumbs')
    uvclight.layer(ICompanyRequest)
    uvclight.baseclass()

    resolver = staticmethod(resolve_name)

    def __init__(self, *args):
        uvclight.Viewlet.__init__(self, *args)


class FlashMessages(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(30)
    uvclight.name('messages')

    template = uvclight.get_template('flashmessages.cpt', __file__)

    def update(self):
        quizzcss.need()
        received = receive()
        if received is not None:
            self.messages = list(received)
        else:
            self.messages = []


@adapter(menus.IContextualActionsMenu, IQuizzLayer)
@implementer(ITemplate)
def object_template(context, request):
    return uvclight.get_template('objectmenu.cpt', __file__)


# class CompanyClassResults(uvclight.Viewlet, Results):
#     uvclight.viewletmanager(IBelowContent)
#     uvclight.view(ClassStats)
#     uvclight.context(IClassSession)
#     uvclight.name('results')

#     template = uvclight.get_template('results.pt', __file__)

#     def display(self):
#         quizzjs.need()
#         data = self.get_data(
#             self.context.course.quizz_type,
#             cid=self.context.course.id,
#             sid=self.context.id,
#             extra_questions=self.context.course.extra_questions)

#         for name, result in data.items():
#             compute_chart = getattr(result, 'compute_chart', None)
#             if compute_chart is None:
#                 yield name, {'results': result.get_answers(),
#                              'total': result.total,
#                              'criterias': result.criterias,
#                              'all': result.total + result.missing,
#                              'users': None, 'chart': None}
#             else:
#                 gbl, users = compute_chart()
#                 yield name, {'results': result.get_answers(),
#                              'total': result.percent_base,
#                              'criterias': result.criterias,
#                              'all': result.percent_base + result.missing,
#                              'users': users,
#                              'chart': gbl}


# class CompanyCourseResults(uvclight.Viewlet, Results):
#     uvclight.viewletmanager(IBelowContent)
#     uvclight.view(CourseStats)
#     uvclight.context(Course)
#     uvclight.name('results')

#     template = uvclight.get_template('results.pt', __file__)

#     def rN(self, value):
#         from nva.psyquizz.models.interfaces import deferred
#         return deferred('quizz_choice')(None).getTerm(self.context.quizz_type).title

#     def display(self):
#         quizzjs.need()
#         data = self.get_data(
#             self.context.quizz_type,
#             cid=self.context.id,
#             extra_questions=self.context.extra_questions)

#         for name, result in data.items():
#             compute_chart = getattr(result, 'compute_chart', None)
#             if compute_chart is None:
#                 yield name, {'results': result.get_answers(),
#                              'total': result.percent_base,
#                              'criterias': result.criterias,
#                              'all': result.percent_base + result.missing,
#                              'users': None, 'chart': None}
#             else:
#                 gbl, users = compute_chart()
#                 yield name, {'results': result.get_answers(),
#                              'total': result.percent_base,
#                              'criterias': result.criterias,
#                              'all': result.percent_base + result.missing,
#                              'users': users,
#                              'chart': gbl}

def colors(limit=15):
    h, s, v = random() * 6, .5, 243.2
    for i in range(limit):
        h += 3.708
        yield ((v,v-v*s*abs(1-h%2),v-v*s)*3)[5**int(h)/3%3::int(h)%2+1][:3]
        if i%5 / 4:
            s += .1
            v -= 51.2


class CompanyCourseDiffs(uvclight.Viewlet, Results):
    uvclight.viewletmanager(IBelowContent)
    uvclight.view(CourseDiff)
    uvclight.context(Course)
    uvclight.name('diffs')

    template = uvclight.get_template('diffs.pt', __file__)

    averages = [
        u'Handlungsspielraum',
        u'Vielseitiges Arbeiten',
        u'Ganzheitliches Arbeiten',
        u'Soziale Rückendeckung',
        u'Zusammenarbeit',
        u'Passende inhaltliche Arbeitsanforderungen',
        u'Passende mengenmäßige Arbeit',
        u'Passende Arbeitsabläufe',
        u'Passende Arbeitsumgebung',
        u'Information und Mitsprache',
        u'Entwicklungsmöglichkeiten',
        ]


    coloring_set = colors()

    @property
    def criterias(self):
        return self.view.criterias
    
    def get_color(self):
        r, v, b = self.coloring_set.next()
        return ['rgba(%i, %i, %i, %s)' % (r, v, b, tr) for tr in [0.3, 1, 1]]

    def display(self):
        quizzjs.need()
        diffs = {}
        for session in self.context.sessions:
            data = self.get_data(
                self.context.quizz_type,
                cid=self.context.id,
                sid=session.id,
                extra_questions=self.context.extra_questions)

            for name, result in data.items():
                diff = diffs.setdefault(name, {})
                gbl, users = result.compute_chart()
                diff['%s - %s' % (session.id, session.startdate)] = gbl
        return diffs


class Home(uvclight.MenuItem):
    uvclight.title(_(u'Startseite'))
    uvclight.auth.require('zope.Public')
    uvclight.menu(INavigationMenu)
    uvclight.layer(ICompanyRequest)
    uvclight.name('index')
    uvclight.order(10)

    def action(self):
        return '%s' % (self.view.application_url())

    @property
    def url(self):
        return self.action()


class PersonalMenuViewlet(PersonalMenuViewlet):
    uvclight.layer(ICompanyRequest)
    template = uvclight.get_template('personalmenuviewlet.cpt', __file__)
    uvclight.auth.require('zope.Public')

    def iavailable(self):
        if self.request.principal.id == "user.unauthenticated":
            return False
        return True


class PiwikStatistik(uvclight.Viewlet):
    uvclight.viewletmanager(IHeaders)
    uvclight.context(Interface)
    template = uvclight.get_template('piwikstatistik.cpt', __file__)


class FavIcon(uvclight.Viewlet):
    uvclight.viewletmanager(IHeaders)
    uvclight.order(0)

    def render(self):
        return '<link rel="shortcut icon" href="%s/fanstatic/nva.psyquizz/favicon.ico" />' % (self.request.host_url)


from uvc.design.canvas import IFooterMenu
class Impressum(uvclight.MenuItem):
    uvclight.menu(IFooterMenu)
    uvclight.context(Interface)
    uvclight.title(u'Impressum')
    uvclight.auth.require('zope.Public')
    #uvclight.layer(ICompanyRequest)

    @property
    def action(self):
        return "http://www.bgetem.de/die-bgetem/impressum"


class Datenschutz(uvclight.MenuItem):
    uvclight.menu(IFooterMenu)
    uvclight.context(Interface)
    uvclight.title(u'Datenschutz')
    uvclight.auth.require('zope.Public')
    #uvclight.layer(ICompanyRequest)

    @property
    def action(self):
        return "https://www.bgetem.de/die-bgetem/impressum/oeffentliches-verfahrensverzeichnis/verfahrensverzeichnis-gemeinsam-zu-gesunden-arbeitsbedingungen-online"


class Kontakt(uvclight.MenuItem):
    uvclight.menu(IFooterMenu)
    uvclight.context(Interface)
    uvclight.title(u'Kontakt')
    uvclight.auth.require('zope.Public')
    uvclight.layer(ICompanyRequest)

    @property
    def action(self):
        return "mailto://gzga@bgetem.de"

