# -*- coding: utf-8 -*-

from . import Base
from .apps import company, anonymous, remote
from collections import namedtuple
from cromlech.configuration.utils import load_zcml
from cromlech.i18n import register_allowed_languages, setLanguage
from cromlech.sqlalchemy import create_engine
from cromlech.sqlalchemy.components import EngineServer
from paste.urlmap import URLMap
from ul.auth import GenericSecurityPolicy
from zope.security.management import setSecurityPolicy


marker = object()


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


def routing(conf, files, session_key, **kwargs):
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

    # Applications configuration
    factory = namedtuple(
        'Setupuration', ('session_key', 'engine', 'name', 'fs_store', 'layer'))
    setup = factory(session_key, engine, name, None, layer_iface)

    # Router
    root = URLMap()
    quizz = localize(anonymous.Application(setup))
    root['/'] = localize(company.Application(setup))
    root['/register'] = localize(company.Registration(setup))
    root['/quizz'] = quizz
    root['/befragung'] = quizz
    root['/json'] = localize(remote.Application(setup))
    return root
