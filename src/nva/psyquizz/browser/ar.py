# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import json
import uvclight

from collections import OrderedDict, namedtuple
from cromlech.sqlalchemy import get_session
from grokcore.component import provider
from nva.psyquizz import hs
from nva.psyquizz.models import IQuizz, IClassSession, ICourse
from nva.psyquizz.models.criterias import CriteriaAnswer
from nva.psyquizz.models.quizz.quizz2 import Quizz2
from sqlalchemy import and_, or_
from sqlalchemy import func
from uvclight.auth import require
from zope.component import getUtility
from zope.interface import Interface
from zope.schema import getFieldsInOrder, Choice
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from ..interfaces import ICompanyRequest


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


def available_criterias(criterias, session_id):
    available_criterias = {}
    Criteria = namedtuple('Criteria', ('id', 'name', 'amount', 'uid'))
    session = get_session('school')
    all_crits = {x[0]: x[1] for x in session.query(
        CriteriaAnswer.answer, func.count(CriteriaAnswer.answer)).filter(
        CriteriaAnswer.session_id == session_id)
                 .group_by(CriteriaAnswer.answer).all()}

    for crit in criterias:
        for item in crit.items.split('\r\n'):
            total = all_crits.get(item, 0)
            if total >= 1:
                uid = '%s:%s' % (crit.id, item)
                criterias = available_criterias.setdefault(crit.title, [])
                criterias.append(Criteria(crit.id, item, total, uid))

    return available_criterias


def compute(quizz, criterias, averages, filters):

    global_data = OrderedDict()
    users_averages = OrderedDict()
        
    session = get_session('school')
    answers = session.query(quizz)
        
    if filters:
        if 'session' in filters:
            answers = answers.filter(
                quizz.session_id == filters['session']
            )

        if 'criterias' in filters:
            # Filter on Criterias
            criterias = (
                and_(quizz.student_id == CriteriaAnswer.student_id,
                     CriteriaAnswer.criteria_id == criteria.id,
                     CriteriaAnswer.answer == criteria.name) for
                criteria in filters['criterias'].values())
            
            answers = answers.filter(or_(*criterias))

    total = answers.count()
    for answer in answers.all():
        user_data = OrderedDict()  # Per user results
        for field, dd in getFieldsInOrder(quizz.__schema__):

            # We cook the result object.
            field_answer = getattr(answer, field, 0)
            result = Result(
                field,
                dd.title,
                field_answer,
                dd.source.getTerm(field_answer).title
            )

            # We set the user response for each question as
            # a list, because we'll use the same method as
            # the global computation for the averages.
            user_data[dd.title] = [Result(
                field,
                dd.title,
                field_answer,
                dd.source.getTerm(field_answer).title
            )]

            # For the global computation
            # We make sure we have the global question set up
            # We'll append all the corresponding answers of all
            # the users
            question = global_data.setdefault(dd.title, [])
            question.append(
                Result(
                    field,
                    dd.title,
                    field_answer,
                    dd.source.getTerm(field_answer).title
                )
            )
        # The computation for a single user is done.
        # We now compute its average.
        sorted_user_answers = sort_data(averages, user_data)
        user_averages = average_computation(sorted_user_answers)
        for av in user_averages:
            group_averages = users_averages.setdefault(av.title, [])
            group_averages.append(av)

    # We do the computation for the global data as well
    sorted_global_answers = sort_data(averages, global_data)
    global_averages = tuple(average_computation(sorted_global_answers))
    
    return {
        'total': total,
        'users.grouped': users_averages,
        'global.averages': global_averages,
    }


class Scale(object):

    percentage = 0
    number = 0
    
    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


def groups_scaling(data):

    groups_scaling = OrderedDict()
    
    for k, av in data.items():
        total = float(len(av))
        scales = (
            Scale('bad', 2.5),
            Scale('mediocre', 3.5),
            Scale('good', 5),
        )
        
        for a in av:
            for scale in scales:
                if a.average <= scale.weight:
                    scale.number += 1
                    break

        for scale in scales:
            scale.percentage = (scale.number / total) * 100

        groups_scaling[k] = scales

    return groups_scaling
        

def radar(data):
    radar_chart = pygal.Radar()
    radar_chart.title = 'RADAR EXAMPLE'
    radar_chart.x_labels = [x.title for x in data]
    radar_chart.add('Chrome',[x.average for x in data])
    return radar_chart.render_data_uri()


def histogramm(data):
    hist = pygal.Histogram()
    hist.add('Wide bars', [(1, 0, 10),  ])
    hist.add('Narrow bars',  [(1, 10, 12), ])
    return hist.render_data_uri()


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


class CourseStatistics(Statistics):

    def __init__(self, quizz, course):
        self.quizz = quizz
        self.course = course
        self.criterias = available_criterias(course.criterias)

    def get_filters(self, request):

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

    def update(self, request):
        self.filters = self.get_filters(request)
        self.statistics = compute(
            self.quizz, self.criterias, self.averages, self.filters)
        #self.radar = radar(self.statistics['global.averages'])
        #self.histogramm = histogramm(None)
        self.users_statistics = groups_scaling(
            self.statistics['users.grouped'])
        self.xAxis = [x.encode('utf-8') for x in self.users_statistics.keys()] 
        good = dict(name="GUT", data=[])
        mid = dict(name="Mittel", data=[])
        bad = dict(name="Schlecht", data=[])
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



import xlsxwriter
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
        self.criterias = available_criterias(session.course.criterias, self.session.id)

    def get_filters(self, request):
        filters = CourseStatistics.get_filters(self, request)
        filters['session'] = self.session.id
        return filters


class SR(uvclight.Page):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    template = uvclight.get_template('cr.pt', __file__)

    def jsonify(self, da):
        return json.dumps(da)

    def update(self):
        hs.need()
        quizz = getUtility(IQuizz, self.context.course.quizz_type)
        self.stats = SessionStatistics(quizz, self.context)
        self.stats.update(self.request)


class CR(uvclight.Page):
    require('manage.company')
    uvclight.context(ICourse)
    uvclight.layer(ICompanyRequest)

    template = uvclight.get_template('cr.pt', __file__)

    def jsonify(self, da):
        return json.dumps(da)

    def update(self):
        hs.need()
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = CourseStatistics(quizz, self.context)
        self.stats.update(self.request)


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
