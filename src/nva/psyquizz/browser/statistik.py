# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

from datetime import datetime
from sqlalchemy import func
from zope import interface
from zope.component import getUtilitiesFor

import uvclight
from uvclight.utils import current_principal
from cromlech.browser import exceptions
from cromlech.sqlalchemy import get_session
from uvclight.auth import require
from nva.psyquizz import models
from nva.psyquizz.models.interfaces import IQuizz
from uvclight import MenuItem
from ..interfaces import ICompanyRequest
from uvc.design.canvas import IFooterMenu


ALLOWED_USERS = {'max.mustermann@bg.de', 'ck@novareto.de', 'ulf.krummreich@vbg.de', 'miriam.rexroth@bgrci.de', 'kuczynski.isabell@bgetem.de'}


class StatstikMenu(MenuItem):
    uvclight.context(interface.Interface)
    uvclight.menu(IFooterMenu)
    uvclight.title(u'Statstik')
    uvclight.layer(ICompanyRequest)

    @property
    def action(self):
        return self.view.application_url() + '/statistik'

    @property
    def available(self):
        if self.request.principal.id in ALLOWED_USERS:
            return True
        return False

class Statistik(uvclight.Page):
    uvclight.context(interface.Interface)
    require('zope.Public')

    template = uvclight.get_template('statistik.cpt', __file__)

    def update(self):
        user = current_principal()
        if not user.id in ALLOWED_USERS:
            raise exceptions.HTTPForbidden('Not allowed.')
        self.session = get_session('school')

    def getAccounts(self):
        return self.session.query(models.Account).count()

    def getCompanies(self):
        return self.session.query(models.Company).count()

    def gCD(self, key):
        dd = {}
        for d in self.getDeletions():
            dd[d[0]] = d[1]
        return dd.get(key, 0)

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
        offen = 0
        closed = 0
        now = datetime.now().date()
        sessions = self.session.query(models.ClassSession).all()
        for session in sessions:
            if session.strategy == "fixed":
                closed += 1
            else:
                offen += 1
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
            offen=offen,
            closed=closed,
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
