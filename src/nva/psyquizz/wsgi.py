# -*- coding: utf-8 -*-

from zope.interface import verify
from zope import interface
interface.verify = verify

import Cookie
from os import path

from collections import namedtuple
from cromlech.configuration.utils import load_zcml
from cromlech.i18n import register_allowed_languages, setLanguage
from cromlech.jwt.components import ExpiredToken
from cromlech.sessions.jwt import JWTCookieSession, key_from_file
from cromlech.sqlalchemy import create_engine
from cromlech.sqlalchemy.components import EngineServer
from paste.urlmap import URLMap
from ul.auth import GenericSecurityPolicy
from zope.security.management import setSecurityPolicy

from . import Base
from .apps import company, anonymous, remote
from .resources import Resources
from .emailer import SecureMailer


marker = object()
Configuration = namedtuple(
    'Configuration', (
        'title',
        'session_key',
        'engine',
        'name',
        'fs_store',
        'layer',
        'reg_layer',
        'emailer',
        'resources',
    )
)


class Session(JWTCookieSession):

    def extract_session(self, environ):
        if 'HTTP_COOKIE' in environ:
            cookie = Cookie.SimpleCookie()
            cookie.load(environ['HTTP_COOKIE'])
            token = cookie.get(self.cookie_name)
            if token is not None:
                try:
                    session_data = self.check_token(token.value)
                    return session_data
                except ExpiredToken:
                    environ['session.timeout'] = True
        return {}


def eval_loader(expr):
    """load  a class / function
    :param expr: dotted name of the module ':' name of the class / function
    :raises RuntimeError: if expr is not a valid expression
    :raises ImportError: if module or object not found
    """
    modname, elt = expr.split(':', 1)
    if modname:
        try:
            module = __import__(modname, {}, {}, ['*'])
            val = getattr(module, elt, marker)
            if val is marker:
                raise ImportError('')
            return val
        except ImportError:
            raise ImportError(
                    "Bad specification %s: no item name %s in %s." %
                    (expr, elt, modname))
    else:
        raise RuntimeError("Bad specification %s: no module name." % expr)


def localize(application):
    def wrapper(*args, **kwargs):
        setLanguage('de')
        return application(*args, **kwargs)
    return wrapper


def routing(conf, files, **kwargs):
    languages = kwargs['langs']
    allowed = languages.strip().replace(',', ' ').split()
    allowed = ('de',)
    register_allowed_languages(allowed)

    load_zcml(kwargs['zcml'])

    setSecurityPolicy(GenericSecurityPolicy)
    name = kwargs.get('name', 'school')

    # We register our SQLengine under a given name
    if not 'engine' in kwargs:
        dsn = kwargs['dsn']
        engine = create_engine(dsn, name)
    else:
        engine = EngineServer(kwargs['engine'], name)

    # We use a declarative base, if it exists we bind it and create
    engine.bind(Base)
    metadata = Base.metadata
    metadata.create_all(engine.engine, checkfirst=True)

    # Extract possible layer
    layer = kwargs.get('layer')
    if layer is not None:
        layer_iface = eval_loader(layer)
    else:
        layer_iface = None
    # Extract possible reg_layer
    reg_layer = kwargs.get('reg_layer')
    if reg_layer is not None:
        reg_layer_iface = eval_loader(reg_layer)
    else:
        reg_layer_iface = None

    title = kwargs.get('title', 'BG ETEM')

    # We create the session wrappper
    session_key = "session"
    key = key_from_file(path.join(kwargs['root'], 'jwt.key'))
    session_wrapper = Session(key, 60, environ_key=session_key)

    # We create the emailer utility
    smtp = kwargs.get('smtp', '10.33.115.55')
    emitter = kwargs.get('emitter', 'my@email.com')
    emailer = SecureMailer(smtp, emitter)

    # Applications configuration
    resources = Resources(kwargs['resources'])
    setup = Configuration(
        title, session_key, engine, name, None, layer_iface, reg_layer_iface, smtp, resources)

    # Router
    root = URLMap()
    quizz = localize(anonymous.Application(setup))
    root['/'] = localize(company.Application(setup))
    root['/register'] = localize(company.Registration(setup))
    root['/quizz'] = quizz
    root['/befragung'] = quizz
    root['/json'] = localize(remote.Application(setup))
    return session_wrapper(root.__call__)
