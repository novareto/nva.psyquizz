# -*- coding: utf-8 -*-

import uvclight

from zope.interface import Interface
from ..i18n import _
from ..interfaces import ICompanyRequest, IQuizzLayer
from .results import Quizz2Charts

from cromlech.browser import IPublicationRoot
from dolmen.breadcrumbs.renderer import BreadcrumbsRenderer
from dolmen.message import receive
from dolmen.template import ITemplate
from grokcore.component import adapter, implementer
from nva.psyquizz import quizzcss
from nva.psyquizz.models.quizz.quizz3 import IQuizz3
from siguvtheme.uvclight.viewlets import PersonalMenuViewlet
from uvc.content import IDescriptiveSchema
from uvc.design.canvas import IAboveContent
from uvc.design.canvas import menus
from uvc.design.canvas.menus import INavigationMenu
from uvc.entities.browser.managers import IHeaders
from cromlech.browser import getSession


def resolve_name(item):
    name = getattr(item, '__name__', None)
    if name is None and not IPublicationRoot.providedBy(item):
        raise KeyError('Object name (%r) could not be resolved.' % item)
    dc = IDescriptiveSchema(item, None)
    if dc is not None:
        return name, dc.title
    return name, name



class Crumbs(BreadcrumbsRenderer, uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(10)
    uvclight.name('crumbs')
    uvclight.layer(ICompanyRequest)
    uvclight.baseclass()

    resolver = staticmethod(resolve_name)

    def __init__(self, *args):
        uvclight.Viewlet.__init__(self, *args)


class Timeout(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(10)
    template = uvclight.get_template('timeout.cpt', __file__)

    def available(self):
        return self.request.environ.get('session.timeout', False)


class Expiration(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(20)
    template = uvclight.get_template('expiration.cpt', __file__)
    expiration = None
    uvclight.baseclass()

    def update(self):
        session = getSession()
        if session is not None:
            self.expiration = session.get('__session_expiration__')


class FlashMessages(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(30)
    uvclight.name('messages')

    template = uvclight.get_template('flashmessages.cpt', __file__)

    def update(self):
        quizzcss.need()
        received = receive()
        if received is not None:
            self.messages = list(received)
        else:
            self.messages = []


@adapter(menus.IContextualActionsMenu, IQuizzLayer)
@implementer(ITemplate)
def object_template(context, request):
    return uvclight.get_template('objectmenu.cpt', __file__)


class Home(uvclight.MenuItem):
    uvclight.title(_(u'Startseite'))
    uvclight.auth.require('zope.Public')
    uvclight.menu(INavigationMenu)
    uvclight.layer(ICompanyRequest)
    uvclight.name('index')
    uvclight.order(10)

    def action(self):
        return '%s' % (self.view.application_url())

    @property
    def url(self):
        return self.action()


class PersonalMenuViewlet(PersonalMenuViewlet):
    uvclight.layer(ICompanyRequest)
    template = uvclight.get_template('personalmenuviewlet.cpt', __file__)
    uvclight.auth.require('zope.Public')

    def iavailable(self):
        if self.request.principal.id == "user.unauthenticated":
            return False
        return True


class PiwikStatistik(uvclight.Viewlet):
    uvclight.viewletmanager(IHeaders)
    uvclight.context(Interface)
    template = uvclight.get_template('piwikstatistik.cpt', __file__)


class FavIcon(uvclight.Viewlet):
    uvclight.viewletmanager(IHeaders)
    uvclight.order(0)

    def render(self):
        return '<link rel="shortcut icon" href="%s/fanstatic/nva.psyquizz/favicon.ico" />' % (self.request.host_url)


from uvc.design.canvas import IFooterMenu
class Impressum(uvclight.MenuItem):
    uvclight.menu(IFooterMenu)
    uvclight.context(Interface)
    uvclight.title(u'Impressum')
    uvclight.auth.require('zope.Public')
    #uvclight.layer(ICompanyRequest)

    @property
    def action(self):
        return "http://www.bgetem.de/die-bgetem/impressum"


class Datenschutz(uvclight.MenuItem):
    uvclight.menu(IFooterMenu)
    uvclight.context(Interface)
    uvclight.title(u'Datenschutz')
    uvclight.auth.require('zope.Public')
    #uvclight.layer(ICompanyRequest)

    @property
    def action(self):
        return "https://www.bgetem.de/die-bgetem/datenschutz/datenschutz-erlaeuterung-gemeinsam-zu-gesunden-arbeitsbedingungen-online"
        #return "https://www.bgetem.de/die-bgetem/impressum/oeffentliches-verfahrensverzeichnis/verfahrensverzeichnis-gemeinsam-zu-gesunden-arbeitsbedingungen-online"


class Kontakt(uvclight.MenuItem):
    uvclight.menu(IFooterMenu)
    uvclight.context(Interface)
    uvclight.title(u'Kontakt')
    uvclight.auth.require('zope.Public')
    uvclight.layer(ICompanyRequest)

    @property
    def action(self):
        return "mailto://gzga@bgetem.de"

