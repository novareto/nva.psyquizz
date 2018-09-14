# -*- coding: utf-8 -*-

import uvclight
from uvclight.auth import require

from cromlech.browser import IRequest
from cromlech.browser import ITraverser
from dolmen.forms.base import FAILURE, SUCCESS
from grokcore.component import MultiAdapter, provides, adapts, name, provider
from nva.psyquizz.models import IQuizz, IClassSession, ICourse, ICompany
from zope.component import queryUtility, getUtilitiesFor
from zope.interface import Interface
from zope.location import Location, LocationProxy
from zope.schema import Choice, Set
from nva.psyquizz import hs
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from .results import CourseStatistics
from ..interfaces import ICompanyRequest


class CompanyCoursesDifference(Location):

    def __init__(self, parent, name, quizz):
        self.__parent__ = parent
        self.__name__ = name
        self.quizz = quizz


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
        title=u"Courses to diff",
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
        if name:
            quizz = queryUtility(IQuizz, name=name)
            if quizz is not None:
                content = CompanyCoursesDifference(
                    self.context, '++diff++' + name, quizz)
                return content
            return None
        return LocationProxy(self, self.context, '++diff++')


class CompanyQuizzDiffs(uvclight.Page):
    name('index')
    require('manage.company')
    uvclight.context(DiffTraverser)
    uvclight.layer(ICompanyRequest)

    template = uvclight.get_template('qdiff.cpt', __file__)

    def update(self):
        url = self.url(self.context)
        self.quizzes = {
            u.__name__: (url + n)
            for n, u in getUtilitiesFor(IQuizz)
            }
        
    
class CompanyDiff(uvclight.Form):
    name('index')
    require('manage.company')
    uvclight.context(CompanyCoursesDifference)
    uvclight.layer(ICompanyRequest)

    fields = uvclight.Fields(IMultipleCoursesDiff)
    fields['courses'].mode = 'multiselect'
    
    template = uvclight.get_template('cdiff.cpt', __file__)
    courses = None
    
    @property
    def action_url(self):
        return self.request.path

    @property
    def label(self):
        return u"Courses difference (%s)" % self.context.quizz.__name__
    
    @uvclight.action(u'Difference')
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
