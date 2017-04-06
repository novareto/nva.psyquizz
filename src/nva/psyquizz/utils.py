# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import uvclight
from uvclight.auth import require
from zope.interface import Interface
from cromlech.sqlalchemy import get_session
from nva.psyquizz.models.criterias import CriteriaAnswer


class Helper(uvclight.View):
    uvclight.context(Interface)
    require('manage.company')

    def render(self):
        session = get_session('school')
        query = session.query(CriteriaAnswer)
        for ca in query:
            sid = ca.student.session_id
            try:
                ca.session_id = int(sid)
            except:
                print ca.student


class HH(Helper):
    uvclight.name('hh')
    uvclight.context(Interface)
    require('manage.company')

    def render(self):
        return ""
