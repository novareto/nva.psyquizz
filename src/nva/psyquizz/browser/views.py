# -*- coding: utf-8 -*-

from datetime import date
import binascii
import base64
from cStringIO import StringIO
import qrcode

from ..i18n import _
from ..interfaces import ICompanyRequest, IRegistrationRequest
from ..interfaces import QuizzAlreadyCompleted, QuizzClosed
from ..models import Company, ClassSession
from uvc.design.canvas import IContextualActionsMenu
from cromlech.browser import getSession
from uvclight import Page, View, MenuItem
from uvclight import layer, title, name, menu, context
from uvclight.auth import require
from zope import interface
from uvc.design.canvas import IFooterMenu
from zope.interface import Interface
from uvc.design.canvas.menus import INavigationMenu
from uvclight import order, get_template
from .. import clipboard_js


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
        if self.context.location.completion_date.date() == date.today():
            return _(u"My message of completion ! THANK YOU")
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
        return u"Ihre Registrierung war erfolgreich. Sie erhalten in Kürze eine \
                 E-Mail mit den Aktivierungslink"


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

    @property
    def template(self):
        template = "example_text.pt"
        if self.context.strategy == "fixed":
            template = "example_text_fixed.pt"
        return get_template(template, __file__)

    def update(self):
        clipboard_js.need()
        Page.update(self)

    def generic_id(self, id):
        return binascii.hexlify(base64.urlsafe_b64encode(str(id) + ' complexificator'))


class QRLink(View):
    context(ClassSession)
    layer(ICompanyRequest)
    require('manage.company')

    def generic_id(self, id):
        return binascii.hexlify(base64.urlsafe_b64encode(str(id) + ' complexificator'))

    def render(self):
        url = '%s/generic-%s' % (
            self.application_url(), self.generic_id(self.context.id))
        img = qrcode.make(url)

        output = StringIO()
        img.save(output, format="PNG")
        output.seek(0)
        return output
        
    def make_response(self, result):
        response = self.responseFactory(app_iter=result)
        response.headers['Content-Type'] = 'image/png'
        response.headers['Content-Disposition'] = (
            'attachment; filename="qrcode.png"')
        return response

from ..interfaces import IAnonymousRequest
from ..apps.anonymous import QuizzBoard
class FinishQuizz(Page):
    context(QuizzBoard)
    layer(IAnonymousRequest)

    def render(self):
        return u"Vielen Danke für die Teilnahme an der Befragung"
