# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from cromlech.sqlalchemy import get_session
from datetime import datetime, timedelta
from nva.psyquizz import models
from nva.psyquizz.models.interfaces import IQuizz
from sqlalchemy import func
from uvclight.auth import require
from zope import interface
from zope.component import getUtilitiesFor


class Statistik(uvclight.Page):
    uvclight.context(interface.Interface)
    require('manage.company')

    template = uvclight.get_template('statistik.cpt', __file__)

    def update(self):
        self.session = get_session('school')

    def getAccounts(self):
        return self.session.query(models.Account).count()

    def getCompanies(self):
        return self.session.query(models.Company).count()

    def getDeletions(self):
        #return session.query(models.HistoryEntry).filter(
        #    models.HistoryEntry.action=="Delete").group_by(
        #        models.HistoryEntry.type).count()
        return self.session.query(
            models.HistoryEntry.type,
            func.count(models.HistoryEntry.type)).group_by(
                models.HistoryEntry.type).filter(
                    models.HistoryEntry.action=="Delete").all()

    def getSessions(self):
        future = 0
        present = 0
        past = 0
        now = datetime.now().date()
        sessions = self.session.query(models.ClassSession).all()

        for session in sessions:
            if session.startdate > now:
                future += 1
            elif now > session.startdate and now < session.enddate:
                present += 1
            elif now > session.enddate:
                past += 1

        return dict(
            alle=len(sessions),
            past=past,
            present=present,
            future=future)

    def getAnswers(self):
        ret = [] 
        for quizz in getUtilitiesFor(IQuizz):
            name, klass = quizz
            ret.append({
                'title': klass.__title__,
                'count': self.session.query(klass).count()
            })
        return ret
