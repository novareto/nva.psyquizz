# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from UserDict import UserDict
from collections import namedtuple
from zope.component import getUtility
from collections import OrderedDict
from nva.psyquizz.models import IQuizz, vocabularies
from nva.psyquizz.models.quizz.quizz5 import IQuizz5
from nva.psyquizz.browser.excel import SessionXSLX, Excel
from nva.psyquizz.browser.results import get_filters
from zope.schema import getFieldsInOrder


def create_options_from_vocabulary(vocabulary):
    options = OrderedDict()
    for option in vocabulary:
        options[option.value] = 0
    return options


class Option(object):
    __slots__ = ('title', 'inverted', 'scale', 'description', 'options')

    def __init__(self, title, description, vocabulary, inverted=False, scale=''):
        self.title = title
        self.inverted = inverted
        self.scale = scale
        self.description = description
        self.options = create_options_from_vocabulary(vocabulary)


class Quizz5Excel(SessionXSLX):
    enable_chart1 = False
    enable_verteilung = False
    enable_ergebnisse = True
    ergebnisse_vocabulary = vocabularies.FBGU

    def generate_ergebnisse(self, workbook):
        ws = workbook.add_worksheet(u'Ergebnisse')

        if hasattr(self.quizz, 'inverted'):
            inverted = dict(list(self.quizz.inverted()))
        else:
            inverted = {}

        averages = self.quizz.__schema__.queryTaggedValue('averages', {})
        xAxis = OrderedDict()

        for id, k in getFieldsInOrder(self.quizz.__schema__):
            xAxis[k.title] = Option(
                k.title, k.description, self.ergebnisse_vocabulary)

        for label, ids in averages.items():
            _, is_inverted = inverted.get(label)
            for id in ids:
                xAxis[id].scale = label
                xAxis[id].inverted = is_inverted

        for key, answers in self.statistics['raw'].items():
            for answer in answers:
                xAxis[key].options[answer.result] += 1

        line = 0
        ws.write(line, 0, 'Frage')
        ws.write(line, 1, 'Scale')
        ws.write(line, 2, 'Inverted')
        ws.write(line, 3, 'Title')
        start = 4
        for option in self.ergebnisse_vocabulary:
            ws.write(line, start, option.title + ' - total')
            start += 1

        for line, option in enumerate(xAxis.values(), 1):
            ws.write(line, 0, option.title)
            ws.write(line, 1, option.scale)
            ws.write(line, 2, option.inverted)
            ws.write(line, 3, option.description)
            for column, count in enumerate(option.options.values(), 4):
                ws.write(line, column, count)


class Excel(Excel):
    uvclight.context(IQuizz5)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = Quizz5Excel(quizz, self.context)
        filters = get_filters(self.request)
        self.stats.update(filters)
