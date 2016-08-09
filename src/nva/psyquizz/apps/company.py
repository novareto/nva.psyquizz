# -*- coding: utf-8 -*-

import os
import webob.exc
import urllib
import urlparse
import html2text

from datetime import datetime
from string import Template

from . import Site
from ..browser.emailer import prepare, SecureMailer, ENCODING
from ..interfaces import ICompanyRequest, IRegistrationRequest
from ..models import Account
from .. import quizzjs, lbg

from cromlech.browser import IPublicationRoot, IView, IResponseFactory
from cromlech.browser.interfaces import ITraverser
from cromlech.security import Interaction, unauthenticated_principal
from cromlech.sqlalchemy import get_session
from dolmen.forms.base import FAILURE, SUCCESS, Fields, SuccessMarker,action
from dolmen.forms.base.errors import Error
from nva.psyquizz import browser
from ul.auth import SecurePublication, ICredentials
from ul.auth import _
from ul.auth.browser import Login, ILoginForm
from ul.browser.context import ContextualRequest
from ul.browser.decorators import sessionned
from ul.browser.publication import Publication
from ul.sql.decorators import transaction_sql
from uvclight import Form
from uvclight import GlobalUtility, Page, MultiAdapter
from uvclight import name, layer, context, baseclass, get_template
from uvclight import provides, adapts, title
from uvclight.auth import require
from uvclight.backends.sql import SQLPublication

from zope.component import getGlobalSiteManager
from zope.interface import Interface, alsoProvides, implementer
from zope.location import Location
from zope.schema import TextLine
from zope.security.proxy import removeSecurityProxy


with open(os.path.join(os.path.dirname(__file__), 'forgotten.tpl'), 'r') as fd:
    data = unicode(fd.read(), 'utf-8')
    forgotten_template = Template(data.encode(ENCODING))


class IActivationRequest(ICompanyRequest):
    pass


class ActivationTraverser(MultiAdapter):
    name('activation')
    adapts(Interface, ICompanyRequest)
    provides(ITraverser)

    def __init__(self, obj, request):
        self.obj = obj
        self.request = request
    
    def traverse(self, ns, name):
        alsoProvides(self.request, IActivationRequest)
        return self.obj


def activate_url(url, **data):
    params = data
    if 'password' in params:
        del params['password']
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(url_parts)

from sqlalchemy import func
@implementer(ICredentials)
class Access(GlobalUtility):
    name('access')
    
    def log_in(self, request, username, password, **kws):
        session = get_session('school')
        account = session.query(Account).filter(
            func.lower(Account.email) == username.lower())

        if account.count() == 1:
            account = account.first()
        else:
            account = None

        if account is not None and account.password == password:
            if account.activated is not None:
                return account
            activation = kws.get('activation')
            if activation is not None:
                if activation == account.activation:
                    account.activated = datetime.now()
                    return account
                else:
                    return SuccessMarker(
                        'Activation failed', False,
                        url=activate_url(request.path, **kws))
            else:
                return SuccessMarker(
                    'Aktivierungs-Key Fehlt', False,
                    url=activate_url(request.path, **kws))
        return None


class IActivation(Interface):
    activation = TextLine(
        title=u'Activation code',
        required=True)
    

def send_forgotten_password(email, password):
    #mailer = SecureMailer('localhost')
    mailer = SecureMailer('smtprelay.bg10.bgfe.local')
    from_ = 'extranet@bgetem.de'
    title = (u'Ihre Passwortanfrage').encode(ENCODING)
    with mailer as sender:
        html = forgotten_template.substitute(
            title=title,
            encoding=ENCODING,
            email=email.encode(ENCODING),
            password=password.encode(ENCODING))

        text = html2text.html2text(html.decode('utf-8'))
        mail = prepare(from_, email, title, html, text.encode('utf-8'))
        print mail.as_string()
        sender(from_, email, mail.as_string())
    return True


class IForgotten(Interface):

    username = TextLine(
        title=_(u"Passwort vergessen"),
        description=_(u'Bitte geben Sie Ihre  E-Mail Adresse ein:'),
        required=True,
        )


class ForgotPassword(Form):
    context(Interface)
    name('forgotten')
    title(_(u'Recover password'))
    require('zope.Public')

    fields = Fields(IForgotten)

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Neues Passwort anfragen'))
    def handle_request(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('school')
        account = session.query(Account).get(data['username'])
        if account is None:
            self.errors.append(
                Error(u'User does not exist',
                      identifier='form.field.username'))
            return FAILURE
        else:
            send_forgotten_password(account.email, account.password)
            self.flash(_(u'Ihr Passwort wurde an Ihre E-Mail-Adresse verschickt.'))
            self.redirect(self.application_url())
            return SUCCESS

    
class AccountLogin(Login):
    name('login')
    layer(ICompanyRequest)
    require('zope.Public')

    prefix = ''
    postOnly = True

    @property
    def action_url(self):
        return self.request.path

    def update(self):
        quizzjs.need()
    
    @property
    def fields(self):
        fields = Login.fields
        fields['username'].title = u"E-Mail"
        fields['came_from'].title = u' '
        if IActivationRequest.providedBy(self.request):
            fields += Fields(IActivation)
            fields['activation'].ignoreRequest = False
            fields['username'].ignoreRequest = False
        for field in fields:
            field.prefix = ''
        return fields

    @action(_(u'Login'))
    def log_me(self):
        result = Login.log_me(self)
        if result.success == True:
            if IActivationRequest.providedBy(self.request):
                return SuccessMarker(
                    'Add a company', True, url='/add.company')
        return result

    def credentials_managers(self):
        yield Access()


class AnonIndex(Page):
    baseclass()
    __component_name__ = 'index'
   
    template = get_template('anon_index_new.pt', browser.__file__)

    def update(self):
        lbg.need()


@implementer(IPublicationRoot, IView, IResponseFactory)
class NoAccess(Location):

    def __init__(self, request):
        self.request = request

    def getSiteManager(self):
        return getGlobalSiteManager()

    def __call__(self):
        if self.request.path_info in (u'/login', u'/++activation++/login'):
            return AccountLogin(self, self.request)()
        if self.request.path_info in (u'/forgotten',):
            return ForgotPassword(self, self.request)()
        return AnonIndex(self, self.request)()


class Application(SQLPublication, SecurePublication):

    layers = [ICompanyRequest]

    def setup_database(self, engine):
        pass

    def principal_factory(self, username):
        principal = SecurePublication.principal_factory(self, username)
        principal.permissions = set(('manage.company',))
        principal.roles = set()
        return principal

    def site_manager(self, request):
        username = request.principal.id.lower()
        if username != unauthenticated_principal.id:
            session = get_session(self.name)
            account = session.query(Account).filter(
                func.lower(Account.email) == username)

            if account.count() == 1:
                account = account.first()
            else:
                account = None

            if account is not None:
                account.getSiteManager = getGlobalSiteManager
                alsoProvides(account, IPublicationRoot)
                return Site(account)
        return Site(NoAccess(request))

    def publish_traverse(self, request):
        user = self.get_credentials(request.environment)
        if user:
            user = user.lower()
        request.principal = self.principal_factory(user)
        try:
            with self.site_manager(request) as site:
                with Interaction(request.principal):
                    response = self.publish(request, site)
                    response = removeSecurityProxy(response)
                    return response
        except webob.exc.HTTPException as e:
            return e

    def __call__(self, environ, start_response):

        @sessionned(self.session_key)
        @transaction_sql(self.engine)
        def publish(environ, start_response):
            layers = self.layers or list()
            with ContextualRequest(environ, layers=layers) as request:
                response = self.publish_traverse(request)
                return response(environ, start_response)

        return publish(environ, start_response)


@implementer(IPublicationRoot)
class Regitration(Publication, Location):

    layers = [IRegistrationRequest]
    
    def __init__(self, session_key, engine):
        self.engine = engine
        self.session_key = session_key

    def getSiteManager(self):
        return getGlobalSiteManager()

    def site_manager(self, request):
        return Site(self)
    
    def __call__(self, environ, start_response):

        @sessionned(self.session_key)
        @transaction_sql(self.engine)
        def publish(environ, start_response):
            layers = self.layers or list()
            with ContextualRequest(environ, layers=layers) as request:
                site_manager = self.site_manager(environ)
                with site_manager as site:
                    response = self.publish_traverse(request, site)
                    return response(environ, start_response)
 
        return publish(environ, start_response)
