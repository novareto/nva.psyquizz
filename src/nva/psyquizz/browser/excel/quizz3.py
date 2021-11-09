# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from collections import OrderedDict
from zope.component import getUtility
from nva.psyquizz.models import IQuizz
from nva.psyquizz.models.quizz.quizz3 import IQuizz3
from nva.psyquizz.browser.excel import SessionXSLX, Excel
from nva.psyquizz.browser.results import get_filters, summing_methods


class Quizz3Excel(SessionXSLX):

    def generateXLSX(self, workbook):
        workbook = super(Quizz3Excel, self).generateXLSX(workbook)
        ws = workbook.add_worksheet('WAI Fragebogen')
        self.board = OrderedDict((
            (u"schlecht", 0),
            (u"mittelmäßig", 0),
            (u"gut", 0),
            (u"sehr gut", 0),
        ))

        results_count = {}
        users_results = {}
        sums = self.statistics['users.sums']
        self.nb_answer = len(sums.values()[0])

        for id, answers in sums.iteritems():
            for idx, answer in enumerate(answers):
                if idx not in users_results:
                    users_results[idx] = 0
                if id in summing_methods:
                    total = summing_methods[id](answer.total)
                else:
                    total = answer.total

                users_results[idx] += total
        summe = 0
        for result in users_results.values():
            if result < 21:
                self.board[u"schlecht"] += 1
            elif result < 28:
                self.board[u"mittelmäßig"] += 1
            elif result < 33:
                self.board[u"gut"] += 1
            else:
                self.board[u"sehr gut"] += 1
            summe += result
            if result not in results_count:
                results_count[result] = 0
            results_count[result] += 1
        self.users_results = users_results
        self.av = float(summe) / len(users_results)
        # Proband
        ws.write(0, 0, u'Proband')
        ws.write(0, 1, u'Punkte')
        index = 1
        for user, value in self.users_results.items():
            ws.write(index, 0, int(user) + 1)
            ws.write(index, 1, value)
            index += 1

        ws.write(index + 3, 0, 'Mittelwerte')
        ws.write(index + 4, 0, 'Durchschnitt')
        ws.write(index + 4, 1, self.av)

        # Mittelwert
        ni = index + 5
        ws.write(ni, 1, u'Punktwertung')
        ws.write(ni, 2, u'Arbeitsfähigkeit')
        ws.write(ni + 1, 1, u'33 bis 36')
        ws.write(ni + 1, 2, u'sehr gut')
        ws.write(ni + 1, 3, self.board.get('sehr gut'))
        ws.write(ni + 2, 1, u'28 bis 32')
        ws.write(ni + 2, 2, u'gut')
        ws.write(ni + 2, 3, self.board.get('gut'))
        ws.write(ni + 3, 1, u'21 bis 27')
        ws.write(ni + 3, 2, u'mittelmäßig')
        ws.write(ni + 3, 3, self.board.get(u'mittelmäßig'))
        ws.write(ni + 4, 1, u'5 bis 20')
        ws.write(ni + 4, 2, u'schlecht')
        ws.write(ni + 4, 3, self.board.get(u'schlecht'))

        # CHART
        chart = workbook.add_chart({'type': 'doughnut'})
        chart.add_series({
            'values': ['WAI Fragebogen', ni+1, 3,  ni+4, 3],
            'categories': ['WAI Fragebogen', ni+1, 2,  ni+4, 2],
            'points': [
                {'fill': {'color': 'green'}},
                {'fill': {'color': 'yellow'}},
                {'fill': {'color': 'orange'}},
                {'fill': {'color': 'red'}},
            ],
        })

        ws.insert_chart("E%s" % ni, chart)
        ws = workbook.add_worksheet('WAI Fragebogen II')
        ws.write(0, 0, u'Summenscore pro Proband')
        ws.write(2, 0, u'Summenscore')
        ws.write(2, 1, u'Anzahl Proband')
        index = 3 
        for score, count in results_count.items():
            ws.write(index, 0, score)
            ws.write(index, 1, count)
            index += 1
        return workbook


class Excel(Excel):
    uvclight.context(IQuizz3)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = Quizz3Excel(quizz, self.context)
        filters = get_filters(self.request)
        self.stats.update(filters)
