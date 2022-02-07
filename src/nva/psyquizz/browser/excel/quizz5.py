# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from zope.component import getUtility
from nva.psyquizz.models import IQuizz
from nva.psyquizz.models.quizz.quizz5 import IQuizz5
from nva.psyquizz.browser.excel import SessionXSLX, Excel
from nva.psyquizz.browser.results import get_filters


class Quizz5Excel(SessionXSLX):
    enable_chart1 = False
    enable_verteilung = False
    enable_ergebnisse = True


class Excel(Excel):
    uvclight.context(IQuizz5)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = Quizz5Excel(quizz, self.context)
        filters = get_filters(self.request)
        self.stats.update(filters)
