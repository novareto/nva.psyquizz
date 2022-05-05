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
    enable_averages = False
    ergebnisse_vocabulary = vocabularies.FBGU

    def generate_mittelwerte(self, workbook):

        if hasattr(self.quizz, 'inverted'):
            inverted = dict(list(self.quizz.inverted()))
        else:
            inverted = {}

        worksheet = workbook.add_worksheet('Mittelwerte')
        nformat = workbook.add_format()
        nformat.set_num_format('0.00')

        # Add a format for the header cells.
        header_format = workbook.add_format({
            'border': 1,
            'bg_color': '#C6EFCE',
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'indent': 1,
            'locked': 1,
        })
        
        question_format = workbook.add_format({
            'border': 0,
            'color': '#000000',
            'bold': True,
            'text_wrap': False,
            'valign': 'vcenter',
            'indent': 0,
            'locked': 1,
        })
        
        def fn(v):
            if v is True:
                return "Resource"
            else:
                return "Belastung"

        worksheet.write(0, 0, 'Bereich')
        worksheet.write(0, 1, 'Mittelwert der Skala')
        worksheet.write(0, 2, 'Resource - hohe Werte wirken positiv auf die Gesundheit')
        for i, x in enumerate(self.statistics['global.averages']):
            worksheet.write(i+1, 0, x.title)
            worksheet.write(i+1, 1, x.average, nformat)
            _, is_inverted = inverted.get(x.title)
            worksheet.write(i+1, 2, fn(is_inverted))
            
        if self.enable_chart1:
            chart1 = workbook.add_chart({'type': 'radar'})
            chart1.add_series({
                'name':       'Mittelwerte',
                'categories': '=Mittelwerte!$A$1:$A$11',
                'values':     '=Mittelwerte!$B$1:$B$11',
                'min': 1,
            })
            
            chart1.set_title({'name': 'Durchschnitt'})
            chart1.set_x_axis({'name': 'Test number', "min": 1})
            chart1.set_y_axis({'name': 'Sample length (mm)', "min": 1})
            chart1.set_style(11)
            
            # Insert the chart into the worksheet (with an offset).
            worksheet.insert_chart(
                'A13', chart1, {'x_offset': 25, 'y_offset': 10})

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
        ws.write(line, 0, 'Frage Nr.')
        ws.write(line, 1, 'Bereich')
        ws.write(line, 2, 'Resource - hohe Werte wirken positiv auf die Gesundheit')
        ws.write(line, 3, 'Frage')
        start = 4
        for option in self.ergebnisse_vocabulary:
            ws.write(line, start, option.title + ' - total')
            start += 1

        def fn(v):
            if v is True:
                return "Resource"
            else:
                return "Belastung"

        for line, option in enumerate(xAxis.values(), 1):
            ws.write(line, 0, option.title)
            ws.write(line, 1, option.scale)
            ws.write(line, 2, fn(option.inverted))
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
