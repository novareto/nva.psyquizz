# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import pygal
import uvclight

from collections import OrderedDict, namedtuple
from cromlech.sqlalchemy import get_session
from nva.psyquizz.models import IQuizz
from nva.psyquizz.models.criterias import CriteriaAnswer
from nva.psyquizz.models.quizz.quizz2 import Quizz2
from sqlalchemy import func
from uvclight.auth import require
from zope.component import getUtility
from zope.interface import Interface
from zope.schema import getFieldsInOrder
from sqlalchemy import and_, or_

from ..interfaces import ICompanyRequest


Result = namedtuple(
    'Result',
    ('answer', 'id', 'result', 'result_title')
)


Average = namedtuple(
    'Average',
    ('title', 'average')
)


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


def available_criterias(criterias):
    available_criterias = {}
    Criteria = namedtuple('Criteria', ('id', 'name', 'amount', 'uid'))
    session = get_session('school')

    all_crits = {x[0]: x[1] for x in session.query(
        CriteriaAnswer.answer, func.count(CriteriaAnswer.answer))
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


from nva.psyquizz import hs


class CR(uvclight.Page):
    uvclight.context(Interface)
    require('manage.company')
    uvclight.layer(ICompanyRequest)
    template = uvclight.get_template('cr.pt', __file__)

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

    def get_filters(self):

        def extract_criteria(str):
            cid, name = str.split(':', 1)
            return str, int(cid), name

        filters = {}
        Criteria = namedtuple('Criteria', ('id', 'name'))
        criterias = self.request.form.get('criterias', None)
        if criterias is not None:
            if not isinstance(criterias, (set, list, tuple)):
                criterias = [criterias]
            filters['criterias'] = {
                uid: Criteria(cid, name) for uid, cid, name in
                map(extract_criteria, criterias)}

        filters['session'] = self.context.id
        return filters

    def update(self):
        hs.need()
        quizz = getUtility(IQuizz, self.context.course.quizz_type)
        self.criterias = available_criterias(self.context.course.criterias)
        self.filters = self.get_filters()
        self.statistics = compute(
            quizz, self.criterias, self.averages, self.filters)
        self.radar = radar(self.statistics['global.averages'])
        self.histogramm = histogramm(None)
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
        import json
        self.series = json.dumps([good, mid, bad])
        self.rd = [x.average for x in self.statistics['global.averages']]
