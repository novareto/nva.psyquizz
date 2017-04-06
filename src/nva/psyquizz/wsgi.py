# -*- coding: utf-8 -*-

from . import Base
from .apps import company, anonymous, remote
from collections import namedtuple
from cromlech.configuration.utils import load_zcml
from cromlech.i18n import register_allowed_languages, setLanguage
from cromlech.sqlalchemy import create_and_register_engine
from paste.urlmap import URLMap
from ul.auth import GenericSecurityPolicy
from zope.i18n import config
from zope.security.management import setSecurityPolicy


def localize(application):
    def wrapper(*args, **kwargs):
        setLanguage('de')
        return application(*args, **kwargs)
    return wrapper


def routing(conf, files, session_key, **kwargs):
    global ALLOWED_LANGUAGES
    languages = kwargs['langs']
    allowed = languages.strip().replace(',', ' ').split()
    allowed = ('de',)
    register_allowed_languages(allowed)
    config.ALLOWED_LANGUAGES = None

    load_zcml(kwargs['zcml'])

    setSecurityPolicy(GenericSecurityPolicy)
    name = 'school'

    # We register our SQLengine under a given name
    dsn = kwargs.get('dsn', "sqlite:////tmp/test.db")
    engine = create_and_register_engine(dsn, name)

    # We use a declarative base, if it exists we bind it and create
    engine.bind(Base)
    metadata = Base.metadata
    metadata.create_all(engine.engine, checkfirst=True)

    # Applications configuration
    factory = namedtuple(
        'Setupuration', ('session_key', 'engine', 'name', 'fs_store'))
    setup = factory(session_key, engine, name, None)

    # Router
    root = URLMap()
    root['/'] = localize(company.Application(setup))
    root['/register'] = localize(company.Registration(setup))
    root['/quizz'] = localize(anonymous.Application(setup))
    root['/json'] = localize(remote.Application(setup))
    return root
