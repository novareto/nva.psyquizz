# -*- coding: utf-8 -*-

import json

from collections import OrderedDict
from ..i18n import _
from ..interfaces import ICompanyRequest, IRegistrationRequest
from ..interfaces import QuizzAlreadyCompleted, QuizzClosed
from ..models import IQuizz, Company, Course, Student, TrueOrFalse
from dolmen.menu import menuentry
from uvc.design.canvas import IContextualActionsMenu
from cromlech.browser import getSession
from uvclight import Page, View, MenuItem
from uvclight import layer, title, name, menu, context, get_template
from uvclight.auth import require
from zope.component import getUtilitiesFor, getUtility
from zope.schema import getFieldsInOrder
from cromlech.sqlalchemy import get_session
from zope import interface
from uvc.design.canvas import IPersonalMenu, IFooterMenu


class LogoutMenu(MenuItem):
    context(interface.Interface)
    menu(IFooterMenu)
    title(u'Abmelden')
    layer(ICompanyRequest)

    @property
    def action(self):
        return self.view.application_url() + '/logout'

    @property
    def available(self):
        if self.request.principal.id == "user.unauthenticated":
            return False
        return True

class Logout(View):
    name(u'logout')
    context(interface.Interface)
    layer(ICompanyRequest)
    require('zope.Public')
   
    def update(self):
        session = getSession()
        if session is not None:
           session.clear()

    def render(self):
        return self.redirect(self.application_url())


class QuizzErrorPage(Page):
    name('')
    context(QuizzAlreadyCompleted)
    require('zope.Public')

    def render(self):
        return _(u"This quizz is already completed and therefore closed.")


class CourseExpiredPage(Page):
    name('')
    context(QuizzClosed)
    require('zope.Public')

    def render(self):
        return _(u"Der Fragebogen ist für den öffentlichen Zugang geschlossen.")


class CriteriasAccess(MenuItem):
    context(Company)
    name('criteria')
    title(_(u'Criterias'))
    layer(ICompanyRequest)
    menu(IContextualActionsMenu)

    @property
    def url(self):
        return self.view.url(self.context) + '/criterias'


class Registered(Page):
    name('registered')
    layer(IRegistrationRequest)
    require('zope.Public')

    def render(self):
        return u"Ihre Registrierung war erfolgreich. Sie erhalten in Kürze eine E-Mail mit den Aktivierungslink"
