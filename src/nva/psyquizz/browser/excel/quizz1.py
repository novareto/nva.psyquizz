# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de
import json
import uvclight
import datetime


from collections import OrderedDict
from zope.component import getUtility
from nva.psyquizz.models import IQuizz
from nva.psyquizz.models.quizz.quizz1 import IQuizz1
from nva.psyquizz.browser.excel import SessionXSLX, Excel, FRONTPAGE
from nva.psyquizz.browser.results import get_filters
from zope.schema import getFieldsInOrder


class Quizz1Excel(SessionXSLX):

    def generateXLSX(self, workbook):
        worksheet0 = workbook.add_worksheet('Dokumentation')
        amounts = dict(json.loads(self.json_criterias))
        db = ""
        if len(self.filters.get('criterias', {})) == 0:
            db = "alle"
        for k,v in self.filters.get('criterias', {}).items():
            db +=  "%s %s" % (v.name, amounts.get(v.name))
        fp = FRONTPAGE % (
            self.course.company.name, 
            self.course.title, 
            self.session.startdate.strftime('%d.%m.%Y'), 
            self.session.enddate.strftime('%d.%m.%Y'),
            db,
            self.statistics.get('total'),
            datetime.datetime.now().strftime('%d.%m.%Y'))
        fm = workbook.add_format()
        fm.set_font_size(16)
        fm.set_text_wrap()
        worksheet0.set_column(0, 0, 130) 

        worksheet0.write(0, 0, fp, fm)
        ws = workbook.add_worksheet(u'Ergebnisse')
        total = 0
        xAxis = []
        good = dict(name="Eher Ja", data=[], color="#62B645")
        bad = dict(name="Eher Nein", data=[], color="#D8262B")
        for key, answers in self.statistics['raw'].items():
            xAxis.append(key)
            yesses = 0
            noes = 0
            total = 0
            for answer in answers:
                total += 1
                if answer.result is True:
                    yesses += 1
                else:
                    noes +=1 

            good['data'].append(float(yesses)/total * 100)
            bad['data'].append(float(noes)/total * 100)
        xAxis_labels = {
            k.title: k.description for id, k in
            getFieldsInOrder(self.quizz.__schema__)}
        for idx in xAxis:
            label = xAxis_labels[idx]
            import pdb; pdb.set_trace()
            goodd = good['data'][int(idx)-1]
            badd = bad['data'][int(idx)-1]
            print label, goodd, badd
        return workbook


class Excel(Excel):
    uvclight.context(IQuizz1)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = Quizz1Excel(quizz, self.context)
        filters = get_filters(self.request)
        self.stats.update(filters)
