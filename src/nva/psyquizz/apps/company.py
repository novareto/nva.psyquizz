# -*- coding: utf-8 -*-

import webob.exc
import hashlib
import urllib
import urlparse

from datetime import datetime
from sqlalchemy import func

from . import Site
from .. import quizzjs, lbg
from ..emailer import ENCODING
from ..interfaces import ICompanyRequest, IRegistrationRequest
from ..models import Account

from cromlech.browser import IPublicationRoot, IView, IResponseFactory
from cromlech.browser.interfaces import ITraverser
from cromlech.security import Interaction, unauthenticated_principal
from cromlech.sqlalchemy import get_session
from dolmen.forms.base import FAILURE, SUCCESS, Fields, SuccessMarker, action
from dolmen.forms.base.errors import Error
from dolmen.message import BASE_MESSAGE_TYPE
from dolmen.message.utils import send
from nva.password.events import PasswordRequestedEvent
from nva.password.interfaces import IPasswordManager
from nva.password.manager import PasswordManagerAdapter
from nva.password.token import ITokenFactory
from nva.psyquizz import browser
from ul.auth import SecurePublication, ICredentials
from ul.auth import _
from ul.auth.browser import Login
from ul.browser.context import ContextualRequest
from ul.browser.decorators import sessionned
from ul.browser.publication import Publication
from ul.sql.decorators import transaction_sql
from uvclight import Form
from uvclight import GlobalUtility, Page, MultiAdapter
from uvclight import name, layer, context, get_template
from uvclight import provides, adapts, title
from uvclight.auth import require
from uvclight.backends.sql import SQLPublication

from zope.component import getGlobalSiteManager, getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.interface import Interface, alsoProvides, implementer
from zope.interface import invariant, Invalid
from zope.location import Location
from zope.schema import TextLine, Password
from zope.security.proxy import removeSecurityProxy


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


def hashed(pwd, salt):
    return hashlib.sha512(pwd + salt).hexdigest()


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
            send(u"Benutzer konnte nicht gefunden werden", BASE_MESSAGE_TYPE)
            return

        if account is not None:
            pwhash = hashed(password, account.salt)
            if account.password == pwhash:
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
        send("Falsches Passwort", BASE_MESSAGE_TYPE)
        return None


class IActivation(Interface):
    activation = TextLine(
        title=u'Activation code',
        required=True)


class AccountPasswordManager(PasswordManagerAdapter):
    context(Account)

    def get_user(self):
        return self.context

    def reset_password(self, newpass, challenge):
        """set new password given valid challenge.
        """
        user = self.get_user()
        tokenizer = getUtility(ITokenFactory, name=self.tokenizer)
        if not tokenizer.verify(user.id, challenge):
            return False
        else:
            return self.set_new_password(user, newpass)

    def request_password_reset(self):
        """sends a challenge to users which will be usable to reset password
        """
        try:
            user = self.get_user()
            tokenizer = getUtility(ITokenFactory, name=self.tokenizer)
            challenge = tokenizer.create(user.id)
            notify(PasswordRequestedEvent(user, challenge))
            return challenge
        except KeyError:
            pass  # silently pass for security sakes

    def set_new_password(self, user, newpass):
        user.password = hashlib.sha512(newpass + user.salt).hexdigest()
        return True


def send_forgotten_password_token(config, account, app_url):
    manager = IPasswordManager(account)
    challenge = manager.request_password_reset()
    namespace = dict(
        title=(u'Ihre Passwortanfrage').encode(ENCODING),
        email=account.email.encode(ENCODING),
        encoding=ENCODING,
        challenge= (
            ("%s/new_password"
             "?form.field.challenge=%s&form.field.username=%s") % (
                 app_url, challenge, account.id)
        ).encode(ENCODING)
    )

    tpl = config.resources.get_template('forgotten.tpl')
    sender = config.emailer.get_sender()
    message = config.emailer.prepare_from_template(
        tpl, account.email, namespace['title'], namespace)
    sender(message)
    return True


class IForgotten(Interface):

    username = TextLine(
        title=_(u"Passwort vergessen"),
        description=_(u'Bitte geben Sie Ihre  E-Mail Adresse ein:'),
        required=True,
        )


class ISetNewPassword(IForgotten):

    challenge = TextLine(
        title=_(u"Challenge"),
        description=_(u'Something in german'),
        required=True,
        )

    new_pass = Password(
        title=_(u"Neues Passwort"),
        description=_(u'Bitte geben Sie hier Ihr neues Passwort ein.'),
        required=True,
        )

    verify_new_pass = Password(
        title=_(u"Passwort bestätigen"),
        description=_(u'Bitte bestätigen Sie hier Ihr neues Passwort.'),
        required=True,
        )

    @invariant
    def verify_pwd(data):
       if data.new_pass != data.verify_new_pass:
            raise Invalid(_(u"Passwort und Wiederholung sind nicht gleich!"))


class ForgotPassword(Form):
    context(Interface)
    name('forgotten')
    title(_(u'Recover password'))
    require('zope.Public')

    fields = Fields(IForgotten)

    @property
    def action_url(self):
        return self.request.path

    def get_user(self, username):
        session = get_session('school')
        username = username
        account = session.query(Account).filter(
            func.lower(Account.email) == username.lower())

        if account.count() == 1:
            return account.first()

        return None

    @action(_(u'Neues Passwort anfragen'))
    def handle_request(self):
        data, errors = self.extractData()
        if errors:
            #self.flash(_(u'Fehlerhafte E-Mail Adresse.'))
            return FAILURE

        account = self.get_user(data['username'])
        if account is None:
            self.errors.append(
                Error(u'Benutzer konnte nicht gefunden werden.',
                      identifier='form.field.username'))
            return FAILURE

        send_forgotten_password_token(
            self.context.configuration,
            account,
            self.application_url()
        )
        self.flash(_(
            u'Ihr Passwort wurde an Ihre E-Mail-Adresse verschickt.'))
        self.redirect(self.application_url())
        return SUCCESS


class SetNewPassword(ForgotPassword):
    name('new_password')
    title(_(u'Set new password'))
    require('zope.Public')

    fields = Fields(ISetNewPassword)

    @action(_(u'Speichern'))
    def handle_request(self):
        data, errors = self.extractData()
        if errors:
            #self.flash(_(u'Fehlerhafte E-Mail Adresse.'))
            return FAILURE

        account = self.get_user(data['username'])
        if account is None:
            return FAILURE
        else:
            manager = IPasswordManager(account)
            manager.reset_password(data['new_pass'], data['challenge'])
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
        if result.success is True:
            if IActivationRequest.providedBy(self.request):
                return SuccessMarker(
                    'Add a company', True, url='/add.company')
        return result

    def credentials_managers(self):
        yield Access()



@implementer(IPublicationRoot, IView, IResponseFactory)
class NoAccess(Location):

    mapping = {
        u"/login": AccountLogin,
        u"/++activation++/login": AccountLogin,
        u"/forgotten": ForgotPassword,
        u"/new_password": SetNewPassword,
    }

    def __init__(self, request, configuration):
        self.request = request
        self.configuration = configuration

    def getSiteManager(self):
        return getGlobalSiteManager()

    def __call__(self):
        if self.request.path_info == '/impressum':
            return getMultiAdapter((self, self.request), name="impressum")()
        elif self.request.path_info == '/datenschutz':
            return getMultiAdapter((self, self.request), name="datenschutz")()
        elif self.request.path_info == '/kontakt':
            return getMultiAdapter((self, self.request), name="kontakt")()
        elif self.request.path_info == '/bf':
            return getMultiAdapter((self, self.request), name="bf")()

        anonview = self.mapping.get(self.request.path_info)
        if anonview is None:
            return getMultiAdapter((self, self.request), name="anonindex")()
        return anonview(self, self.request)()


class AnonIndex(Page):
    context(NoAccess)

    template = get_template('anon_index_new.pt', browser.__file__)

    def update(self):
        lbg.need()


class Application(SQLPublication, SecurePublication):

    _layers = [ICompanyRequest]

    @property
    def layers(self):
        if self.configuration.layer is not None:
            return [self.configuration.layer] + self._layers
        return self._layers

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
            session = get_session(self.configuration.name)
            account = session.query(Account).filter(
                func.lower(Account.email) == username)

            if account.count() == 1:
                account = account.first()
            else:
                account = None
            if account is not None:
                account.configuration = self.configuration
                account.getSiteManager = getGlobalSiteManager
                alsoProvides(account, IPublicationRoot)
                return Site(account)
        return Site(NoAccess(request, self.configuration))

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

        @sessionned(self.configuration.session_key)
        @transaction_sql(self.configuration.engine)
        def publish(environ, start_response):
            layers = self.layers or list()
            with ContextualRequest(environ, layers=layers) as request:
                response = self.publish_traverse(request)
                return response(environ, start_response)

        return publish(environ, start_response)


@implementer(IPublicationRoot)
class Registration(Publication, Location):

    _layers = [IRegistrationRequest]

    @property
    def layers(self):
        if self.configuration.reg_layer is not None:
            return [self.configuration.reg_layer, self.configuration.layer] + self._layers
        return self._layers

    def __init__(self, configuration):
        self.configuration = configuration

    def getSiteManager(self):
        return getGlobalSiteManager()

    def site_manager(self, request):
        return Site(self)

    def __call__(self, environ, start_response):

        @sessionned(self.configuration.session_key)
        @transaction_sql(self.configuration.engine)
        def publish(environ, start_response):
            layers = self.layers or list()
            with ContextualRequest(environ, layers=layers) as request:
                site_manager = self.site_manager(environ)
                with site_manager as site:
                    response = self.publish_traverse(request, site)
                    return response(environ, start_response)

        return publish(environ, start_response)
