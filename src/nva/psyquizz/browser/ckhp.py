# -*- coding: utf-8 -*-

import base64
import datetime
import binascii
from .. import quizzjs, clipboard_js
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..models import Account, ClassSession
from ..models.deferred import quizz_choice
from uvclight import Page, MenuItem
from uvclight import order, layer, name, menu, view, context, title, get_template
from uvclight.auth import require
from uvc.design.canvas.menus import INavigationMenu
from zope.interface import Interface


class AccountHomepage(Page):
    name('index')
    title(_(u'Frontpage'))
    context(Account)
    layer(ICompanyRequest)
    require('manage.company')

    template = get_template('ckh.pt', __file__)

    def update(self):
        quizzjs.need()

    def quizz_name(self, course):
        voc = quizz_choice(course)
        return voc.getTermByToken(course.quizz_type).title

    def generic_id(self, id):
        return binascii.hexlify(base64.urlsafe_b64encode(str(id) + ' complexificator'))

    def checkDate(self, date):
        now = datetime.datetime.now()
        if date < now.date():
            return True
        return False


class SevenSteps(MenuItem):
    context(Interface)
    layer(ICompanyRequest)
    menu(INavigationMenu)
    order(100)
    require('manage.company')
    title(u'Übersicht 7 Schritte')

    @property
    def url(self):
        return "https://www.bgetem.de/arbeitssicherheit-gesundheitsschutz/themen-von-a-z-1/psychische-belastung-und-beanspruchung/gemeinsam-zu-gesunden-arbeitsbedingungen-beurteilung-psychischer-belastung"


class SevenStepsView(Page):
    name('sevensteps')
    context(Interface)
    layer(ICompanyRequest)
    require('manage.company')
    template = get_template('sevensteps.pt', __file__)

    @property
    def panel(self):
        template = get_template('anon_index.pt', __file__)
        panel = template.macros['panel']
        return panel

class ExampleText(Page):
    context(ClassSession)
    layer(ICompanyRequest)
    require('manage.company')
    template = get_template('example_text.pt', __file__)

    def update(self):
        clipboard_js.need()
        Page.update(self)

    def generic_id(self, id):
        return binascii.hexlify(base64.urlsafe_b64encode(str(id) + ' complexificator'))
