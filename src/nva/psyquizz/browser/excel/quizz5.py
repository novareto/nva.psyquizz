# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de
import json
import uvclight
import datetime


from collections import OrderedDict
from zope.component import getUtility
from nva.psyquizz.models import IQuizz
from nva.psyquizz.models.quizz.quizz5 import IQuizz5
from nva.psyquizz.browser.excel import SessionXSLX, Excel, FRONTPAGE
from nva.psyquizz.browser.excel import quizz1
from nva.psyquizz.browser.results import get_filters
from zope.schema import getFieldsInOrder


class Quizz5Excel(SessionXSLX):
    enable_chart1 = False


class Excel(Excel):
    uvclight.context(IQuizz5)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = Quizz5Excel(quizz, self.context)
        filters = get_filters(self.request)
        self.stats.update(filters)
