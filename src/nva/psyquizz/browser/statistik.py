# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from zope import interface
from uvclight.auth import require
from cromlech.sqlalchemy import get_session
from nva.psyquizz import models
from datetime import datetime, timedelta


class Statistik(uvclight.Page):
    uvclight.context(interface.Interface)
    require('manage.company')

    template = uvclight.get_template('statistik.cpt', __file__)

    def getAccounts(self):
        session = get_session('school')
        return session.query(models.Account).count()

    def getCompanies(self):
        session = get_session('school')
        return session.query(models.Company).count()

    def getSessions(self):
        future = 0
        present = 0
        past = 0
        session = get_session('school')
        now = datetime.now().date()
        sessions = session.query(models.ClassSession).all()

        for session in sessions:
            if session.startdate > now:
                future += 1
            elif now > session.startdate and now < session.startdate + timedelta(days=session.duration):
                present += 1
            elif now > session.startdate + timedelta(days=session.duration):
                past += 1
        return dict(alle=len(sessions), past=past, present=present, future=future)

    def getAnswers(self):
        session = get_session('school')
        from nva.psyquizz.models.quizz.quizz2 import Quizz2
        return session.query(Quizz2).count()

