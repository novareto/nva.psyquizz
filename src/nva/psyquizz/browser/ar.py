# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import json
import uvclight
import xlsxwriter

from collections import OrderedDict, namedtuple
from cromlech.browser import IView
from grokcore.component import name, provider
from nva.psyquizz import hs
from nva.psyquizz.models import IQuizz, IClassSession, ICourse
from nva.psyquizz.models.quizz.quizz2 import Quizz2
from nva.psyquizz.models.quizz.quizz1 import Quizz1
from uvclight.auth import require
from zope.component import getUtility, getMultiAdapter
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.location import LocationProxy

from ..interfaces import ICompanyRequest
from ..stats import compute, available_criterias, groups_scaling
from zope.schema import Choice
from dolmen.forms.base import FAILURE, SUCCESS
from nva.psyquizz.i18n import MessageFactory as _


Result = namedtuple(
    'Result',
    ('answer', 'id', 'result', 'result_title'))


Average = namedtuple(
    'Average',
    ('title', 'average'))


def average_computation(data):
    for k, v in data.items():
        yield Average(k, float(sum([x.result for x in v]))/len(v))    


def sort_data(order, data):

    def sorter(id):
        for k, v in order.items():
            if id in v:
                return k

    ordered = OrderedDict()
    for id, values in data.items():
        title = sorter(id)
        current = ordered.setdefault(title, [])
        current += values

    return ordered


class Scale(object):

    percentage = 0
    number = 0

    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


class Statistics(object):

    averages = OrderedDict((
        (u'Vielseitiges Arbeiten', ('1', '2', '3')),
        (u'Ganzheitliches Arbeiten', ('4', '5')),
        (u'Passende inhaltliche Arbeitsanforderungen', ('6', '7')),
        (u'Passende mengenmäßige Arbeit', ('8', '9')),
        (u'Passende Arbeitsabläufe', ('10', '11')),
        (u'Passende Arbeitsumgebung', ('12', '13')),
        (u'Handlungsspielraum', ('14', '15', '16')),
        (u'Soziale Rückendeckung', ('17', '18', '19')),
        (u'Zusammenarbeit', ('20', '21', '22')),
        (u'Information und Mitsprache', ('23', '24')),
        (u'Entwicklungsmöglichkeiten', ('25', '26')),
        ))


def get_filters(request):

    def extract_criteria(str):
        cid, name = str.split(':', 1)
        return str, int(cid), name

    filters = {}
    Criteria = namedtuple('Criteria', ('id', 'name'))
    criterias = request.form.get('criterias', None)
    if criterias is not None:
        if not isinstance(criterias, (set, list, tuple)):
            criterias = [criterias]
        filters['criterias'] = {
            uid: Criteria(cid, name) for uid, cid, name in
            map(extract_criteria, criterias)}
    return filters


class CourseStatistics(object):

    def __init__(self, quizz, course):
        self.quizz = quizz
        self.averages = quizz.__schema__.getTaggedValue('averages')
        self.course = course
        session_ids = [x.id for x in self.course.sessions]
        self.criterias = available_criterias(course.criterias, session_ids)

    def update(self, filters):
        self.filters = filters
        self.statistics = compute(
            self.quizz, self.criterias, self.averages, self.filters)
        self.users_statistics = groups_scaling(
            self.statistics['users.grouped'])
        self.xAxis = [
            x.encode('utf-8') for x in self.users_statistics.keys() if x] 
        good = dict(name="GUT", data=[], color="#62B645")
        mid = dict(name="Mittel", data=[], color="#FFCC00")
        bad = dict(name="Schlecht", data=[], color="#D8262B")
        for x in self.users_statistics.values():
            good['data'].append(x[0].percentage)
            mid['data'].append(x[1].percentage)
            bad['data'].append(x[2].percentage)
        self.series = json.dumps([good, mid, bad])
        self.rd = [x.average for x in self.statistics['global.averages']]

        criterias = []
        for crits in self.criterias.values():
            for crit in crits:
                criterias.append([crit.name, crit.amount])
        self.json_criterias = json.dumps(criterias)


class XLSX(CourseStatistics):

    def generateXLSX(self):
        workbook = xlsxwriter.Workbook('/tmp/ouput.xlsx')
        worksheet = workbook.add_worksheet() 
        for i, x in enumerate(self.statistics['global.averages']):
            worksheet.write(i, 0, x.title)
            worksheet.write(i, 1, x.average)
        chart1 = workbook.add_chart({'type': 'radar'})
        chart1.add_series({
            'name':       'KLAUS',
            'categories': '=Sheet1!$A$1:$A$11',
            'values':     '=Sheet1!$B$1:$B$11',
            })

        chart1.set_title ({'name': 'Results of sample analysis'})
        chart1.set_x_axis({'name': 'Test number'})
        chart1.set_y_axis({'name': 'Sample length (mm)'})
        chart1.set_style(11)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})

        workbook.close()

    def render(self):
        self.generateXLSX()
        import pdb; pdb.set_trace() 


class SessionStatistics(CourseStatistics):

    def __init__(self, quizz, session):
        self.quizz = quizz
        self.course = session.course
        self.session = session
        self.averages = quizz.__schema__.getTaggedValue('averages')
        self.criterias = available_criterias(
            session.course.criterias, [self.session.id, ])

    def update(self, filters):
        filters['session'] = self.session.id
        return CourseStatistics.update(self, filters)


class Quizz2Charts(uvclight.Page):
    require('manage.company')
    name('charts')
    uvclight.context(Quizz2)

    template = uvclight.get_template('cr.pt', __file__)
    general_stats = None

    def jsonify(self, da):
        return json.dumps(da)

    def update(self, stats, general_stats=None):
        hs.need()
        self.stats = stats
        self.general_stats = general_stats


class Quizz1Charts(uvclight.Page):
    require('manage.company')
    name('charts')
    uvclight.context(Quizz1)

    template = uvclight.get_template('cr.pt', __file__)

    def jsonify(self, da):
        return json.dumps(da)

    def update(self, stats, general_stats=None):
        hs.need()
        self.stats = stats
        self.general_stats = general_stats


class SR(uvclight.Page):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)
 
    def update(self):
        quizz = getUtility(IQuizz, self.context.course.quizz_type)
        filters = get_filters(self.request)
        stats = SessionStatistics(quizz, self.context)
        stats.update(filters)

        if 'criterias' in filters:
            general_stats = SessionStatistics(quizz, self.context)
            general_stats.update({})
        else:
            general_stats = None

        quizz_obj = LocationProxy(quizz(), container=self.context, name='')
        self.charts = getMultiAdapter(
            (quizz_obj, self.request), IView, name="charts")
        self.charts.update(stats, general_stats)

    def render(self):
        return self.charts.render()


class CR(uvclight.Page):
    require('manage.company')
    uvclight.context(ICourse)
    uvclight.layer(ICompanyRequest)

    template = uvclight.get_template('cr.pt', __file__)
    general_stats = None

    def jsonify(self, da):
        return json.dumps(da)

    def update(self):
        hs.need()
        quizz = getUtility(IQuizz, self.context.quizz_type)
        filters = get_filters(self.request)
        stats = CourseStatistics(quizz, self.context)
        stats.update(filters)

        if 'criterias' in filters:
            general_stats = CourseStatistics(quizz, self.context)
            general_stats.update({})
        else:
            general_stats = None

        self.charts = getMultiAdapter(
            (quizz, self.request), IView, name="charts")
        self.charts.update(stats, general_stats)

    def render(self):
        return self.charts.render()


@provider(IContextSourceBinder)
def courses(context):
    return SimpleVocabulary([
        SimpleTerm(value=c, token=c.id, title=c.name)
        for c in context.company.courses if c.id != context.id])


class ICourseDiff(Interface):

    course = Choice(
        title=u"Course to diff with",
        required=True,
        source=courses)


class CDiff(uvclight.Form):
    require('manage.company')
    uvclight.context(ICourse)
    uvclight.layer(ICompanyRequest)

    fields = uvclight.Fields(ICourseDiff)
    template = uvclight.get_template('cdiff.cpt', __file__)

    current = None
    diff = None

    @property
    def action_url(self):
        return self.request.path

    @uvclight.action(u'Difference')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        hs.need()
        quizz = getUtility(IQuizz, self.context.quizz_type)
        # This course
        self.current = CourseStatistics(quizz, self.context)
        self.current.update(self.request)

        # The diff course
        self.diff = CourseStatistics(quizz, data['course'])
        self.diff.update(self.request)
        return SUCCESS