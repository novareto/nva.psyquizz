# -*- coding: utf-8 -*-

import uvclight
from uvclight.auth import require

from cromlech.browser import IRequest, ITraverser
from dolmen.forms.base import FAILURE, SUCCESS
from grokcore.component import MultiAdapter, provides, adapts, name, provider
from nva.psyquizz import hs
from nva.psyquizz.models import IQuizz, IClassSession, ICourse, ICompany
from uvc.design.canvas import IAboveContent
from zope.component import queryUtility, getUtilitiesFor
from zope.interface import Interface
from zope.location import Location, LocationProxy
from zope.schema import Choice, Set
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from collections import OrderedDict

from .results import CourseStatistics
from ..interfaces import ICompanyRequest
from ..i18n import _


class CompanyCoursesDifference(Location):

    def __init__(self, parent, name, quizz, quizzes):
        self.__parent__ = parent
        self.__name__ = name
        self.quizz = quizz
        self.quizzes = quizzes


@provider(IContextSourceBinder)
def courses(context):
    if isinstance(context, CompanyCoursesDifference):
        voc = SimpleVocabulary([
            SimpleTerm(value=c, token=c.id, title=c.name)
            for c in context.__parent__.courses
            if c.quizz_type == context.quizz.__tablename__])
        return voc
    raise NotImplementedError


class IMultipleCoursesDiff(Interface):

    courses = Set(
        title=_(u"Courses to diff"),
        value_type=Choice(source=courses),
        required=True,
        )


class DiffTraverser(MultiAdapter):
    name('diff')
    adapts(ICompany, IRequest)
    provides(ITraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, ns, name):
        def sorter(a, b):
            return cmp(a[0], b[0])

        quizzes = list(getUtilitiesFor(IQuizz))
        if quizzes:
            quizzes.sort(sorter)
            self.quizzes = OrderedDict(quizzes)

            if not name:
                name, quizz = quizzes[0]
            else:
                quizz = self.quizzes[name]

            return CompanyCoursesDifference(
                self.context, '++diff++' + name, quizz, self.quizzes)
        return None
        
    
class CompanyDiff(uvclight.Form):
    name('index')
    require('manage.company')
    uvclight.context(CompanyCoursesDifference)
    uvclight.layer(ICompanyRequest)

    fields = uvclight.Fields(IMultipleCoursesDiff)
    #fields['courses'].mode = 'multiselect'
    
    template = uvclight.get_template('cdiff.cpt', __file__)
    courses = None
    inline = False
    
    @property
    def action_url(self):
        return self.request.path

    @property
    def label(self):
        return _(u"Courses difference (${quizz})",
                 mapping={'quizz': self.context.quizz.__name__})
    
    @uvclight.action(_(u'Difference'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        hs.need()

        self.courses = []
        for course in data['courses']:
            stat = CourseStatistics(self.context.quizz, course)
            stat.update({'course': course.id})
            self.courses.append(stat)
            
        return SUCCESS

    @uvclight.action(u'Export')
    def handle_export(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        view = getMultiAdapter(
            (self.context, self.request), name="excel")
        view.update()
        return SUCCESS


class DiffTabs(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(10)
    uvclight.name('diff-tabs')
    uvclight.layer(ICompanyRequest)
    uvclight.context(CompanyCoursesDifference)
    template = uvclight.get_template('difftabs.cpt', __file__)

    def update(self):
        url = self.view.url(self.context.__parent__)
        self.quizzes = (
            ('%s/++diff++%s' % (url, n), u)
            for n, u in self.context.quizzes.items())
