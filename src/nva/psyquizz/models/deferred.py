# -*- coding: utf-8 -*-

from .interfaces import IQuizz, IQuizzSecurity, ICompany
from .criterias import Criteria
from . import Account, Company
from . import deferred_vocabularies
from cromlech.sqlalchemy import get_session
from grokcore.component import provider, queryOrderedSubscriptions
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


def check_quizz(name, quizz, context):
    subs = queryOrderedSubscriptions(quizz, IQuizzSecurity)
    for sub in subs:
        success = sub.check(name, quizz, context)
        if not success:
            return False
    return True


@provider(IContextSourceBinder)
def quizz_choice(context):
    terms = []
    utils = getUtilitiesFor(IQuizz)
    for name, quizz in utils:
        if check_quizz(name, quizz, context):
            terms.append(SimpleTerm(value=name, title=quizz.__title__))
    return SimpleVocabulary(terms)


@provider(IContextSourceBinder)
def quizz_choice_full(context):
    terms = []
    utils = getUtilitiesFor(IQuizz)
    for name, quizz in utils:
        terms.append(SimpleTerm(value=name, title=quizz.__title__))
    return SimpleVocabulary(terms)

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
