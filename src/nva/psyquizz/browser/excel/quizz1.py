# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import json
import uvclight
import datetime

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
            db +=  "%s" % (v.name)
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
        self.generate_ergebnisse(workbook)
        if self.statistics['extra_data']:
            line = 0
            worksheet = workbook.add_worksheet('Zusatzfragen')

            for label, answers in self.extra_questions_order.items():
                value = self.statistics['extra_data'][label]
                worksheet.write(line, 0, label)
                col = 1
                for answer in answers:
                    worksheet.write(line + 0, col, answer)
                    worksheet.write(line + 1, col, value.get(answer, 0))
                    col += 1
                line += 4
        return workbook


class Excel(Excel):
    uvclight.context(IQuizz1)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = Quizz1Excel(quizz, self.context)
        filters = get_filters(self.request)
        self.stats.update(filters)
