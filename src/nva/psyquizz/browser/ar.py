# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from uvclight.auth import require

from zope.interface import Interface
from ..interfaces import ICompanyRequest
from cromlech.sqlalchemy import get_session
from nva.psyquizz.models.quizz.quizz2 import Quizz2
from nva.psyquizz.models.criterias import CriteriaAnswer
from nva.psyquizz.models import IQuizz
from collections import OrderedDict
from zope.component import getUtility

from zope.schema import getFieldsInOrder
from collections import namedtuple
import pygal


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


    def getRadar(self):
        radar_chart = pygal.Radar()
        radar_chart.title = 'RADAR EXMAPLE'
        data = self.getPData()
        radar_chart.x_labels = [x.name for x in self.getPData()]
        radar_chart.add('Chrome',[x.value for x in self.getPData()])
        return radar_chart.render_data_uri()

    def update(self):
        self.quizz = getUtility(IQuizz, self.context.course.quizz_type)
        self.data = self.getBaseData()
        self.avdata = self.getAverageData()
        self.criterias = self.getCriterias()

    def getCriterias(self):
        d = {}
        CRIT = namedtuple('Criterias', ('name', 'amount'))
        session = get_session('school')
        from sqlalchemy import func
        all_crits = {x[0]: x[1] for x in session.query(CriteriaAnswer.answer, func.count(CriteriaAnswer.answer)).group_by(CriteriaAnswer.answer).all()}
        for crit in self.context.course.criterias:
            d[crit.title] = []
            print crit.title
            for item in crit.items.split('\r\n'):
                d[crit.title].append(CRIT(item, all_crits.get(item, 0)))
        print d
        return d

    def getPData(self):
        PR = namedtuple('PrintResults', ('name', 'value'))
        for k, v in self.avdata.items():
            yield PR(k, float(sum([x.result for x in v]))/len(v))

    def getAverageData(self):
        def getAV(question_id):
            for k, v in self.averages.items():
                if question_id in v:
                    return k
        av = {}
        for question_id, questions in self.data.items():
            average = getAV(question_id)
            if average not in av.keys():
                av[average] = []
            av[average] += questions
        return av

    def getBaseData(self):
        Result = namedtuple(
            'Result',
            ('answer', 'id', 'result', 'result_title')
        )
        data = {}
        session = get_session('school')
        answers = session.query(Quizz2).filter(
            Quizz2.session_id == self.context.id
        )
        if False:  # Filter on Criterias
            answers = answers.filter(
                Quizz2.student_id == CriteriaAnswer.student_id,
                CriteriaAnswer.answer == "HR"
            )
        for answer in answers.all():
            for field, dd in getFieldsInOrder(self.quizz.__schema__):
                if dd.title not in data.keys():
                    data[dd.title] = []
                field_answer = getattr(answer, field, 0)
                data[dd.title].append(
                    Result(
                        field,
                        dd.title,
                        field_answer,
                        dd.source.getTerm(field_answer).title
                    )
                )
        return data
