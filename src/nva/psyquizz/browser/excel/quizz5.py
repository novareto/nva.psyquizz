# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from UserDict import UserDict
from collections import namedtuple
from zope.component import getUtility
from nva.psyquizz.models import IQuizz, vocabularies
from nva.psyquizz.models.quizz.quizz5 import IQuizz5
from nva.psyquizz.browser.excel import SessionXSLX, Excel
from nva.psyquizz.browser.results import get_filters
from zope.schema import getFieldsInOrder


class Option(object):
    __slots__ = ('title', 'value')

    def __init__(self, title, value=None):
        self.title = title
        self.value = value


class Quizz5Excel(SessionXSLX):
    enable_chart1 = False
    enable_verteilung = False
    enable_ergebnisse = True
    ergebnisse_vocabulary = vocabularies.FBGU

    def generate_ergebnisse(self, workbook):
        ws = workbook.add_worksheet(u'Ergebnisse')
        total = 0
        xAxis = []

        averages = self.quizz.__schema__.queryTaggedValue('averages')
        if averages:
            avg_labels = {}
            for label, ids in averages.items():
                avg_labels.update({id: Option(label) for id in ids})

        if hasattr(self.quizz, 'inverted'):
            inverted = dict(list(self.quizz.inverted()))
        else:
            inverted = {}

        for key, answers in self.statistics['raw'].items():
            xAxis.append(key)
            for answer in answers:
                avg_labels[key].value = answer.result

        xAxis_labels = {
            k.title: k.description for id, k in
            getFieldsInOrder(self.quizz.__schema__)}
        line = 0
        ws.write(line, 0, 'Frage')
        ws.write(line, 1, 'Scale')
        ws.write(line, 2, 'Inverted')
        ws.write(line, 3, 'Title')
        start = 4
        for option in self.ergebnisse_vocabulary:
            ws.write(line, start, option.title + ' - total')
            start += 1

        line = 1
        for idx in xAxis:
            ws.write(line, 0, xAxis_labels[idx])
            if averages:
                label, is_inverted = inverted.get(avg_labels[idx].title)
                ws.write(line, 1, avg_labels[idx].title)
                ws.write(line, 2, is_inverted)
                ws.write(line, 3, label)
                start = 4
                for option in self.ergebnisse_vocabulary:
                    if option.value == avg_labels[idx].value:
                        ws.write(line, start + 1, 1)
                    start += 1

            line += 1


class Excel(Excel):
    uvclight.context(IQuizz5)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = Quizz5Excel(quizz, self.context)
        filters = get_filters(self.request)
        self.stats.update(filters)
