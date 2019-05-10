# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import uvclight
from uvclight.auth import require
from zope.interface import Interface
from cromlech.sqlalchemy import get_session
from nva.psyquizz.models.quizz.quizz2 import Quizz2
from nva.psyquizz.models.session import ClassSession 



class Helper(uvclight.View):
    uvclight.context(Interface)
    require('manage.company')

    def render(self):
        session = get_session('school')
        query = session.query(Quizz2).filter(Quizz2.course_id == None)
        print query.count()
        for ii in query.all():
            ses = session.query(ClassSession).get(ii.session_id)
            if ses:
                ii.course_id = ses.course_id
                print ii


class HH(Helper):
    uvclight.name('hh')
    uvclight.context(Interface)
    require('manage.company')

    def render(self):
        return ""
