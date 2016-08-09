# -*- coding: utf-8 -*-

from .interfaces import IQuizz, ICompany
from .criterias import Criteria
from . import Account, Company
from . import deferred_vocabularies
from cromlech.sqlalchemy import get_session
from grokcore.component import provider
from zope.component import getUtilitiesFor
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from uvclight import getRequest


def get_company_id(node):
    current = node
    while current is not None:
        if ICompany.providedBy(current):
            return current
        current = getattr(current, '__parent__', None)
    raise RuntimeError('No company found')


@provider(IContextSourceBinder)
def quizz_choice(context):
    utils = getUtilitiesFor(IQuizz)
    return SimpleVocabulary([
        SimpleTerm(value=name, title=obj.__title__) for name, obj in utils
    ])


@provider(IContextSourceBinder)
def criterias_choice(context):
    session = get_session('school')
    company = get_company_id(context)
    criterias = session.query(Criteria).filter(
        Criteria.company_id == company.id)
    return SimpleVocabulary([
        SimpleTerm(value=c, token=c.id, title=c.title)
        for c in criterias])


@provider(IContextSourceBinder)
def accounts_choice(context):
    session = get_session('school')
    accounts = session.query(Account).all()
    return SimpleVocabulary([
        SimpleTerm(value=c.email, token=c.email,
                   title='%s (%s)' % (c.name, c.email))
        for c in accounts])


@provider(IContextSourceBinder)
def companies_choice(context):
    request = getRequest()
    session = get_session('school')
    accounts = session.query(Company).filter(Company.account_id == request.principal.id).all()
    return SimpleVocabulary([
        SimpleTerm(value=c, token=c.id,
                   title='%s (%s)' % (c.name, c.account_id))
        for c in accounts])


deferred_vocabularies['quizz_choice'] = quizz_choice
deferred_vocabularies['accounts_choice'] = accounts_choice
deferred_vocabularies['criterias_choice'] = criterias_choice
deferred_vocabularies['companies_choice'] = companies_choice
