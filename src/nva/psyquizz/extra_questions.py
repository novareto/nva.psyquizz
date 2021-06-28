# -*- coding: utf-8 -*-

import re
from .models import TrueOrFalse
from zope.schema import Set, Choice
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


def make_boolean_field(idx, question, *_):
    field = Choice(
        __name__='extra_question%s' % idx,
        title=unicode(idx),
        description=question,
        vocabulary=TrueOrFalse,
        required=True,
    )
    return field


def make_choice_field(idx, question, *choices):
    vocabulary = SimpleVocabulary([
        SimpleTerm(title=c, token='%s-%s' % (idx, n), value=c)
        for n, c in enumerate(choices)
    ])
    field = Choice(
        __name__='extra_question%s' % idx,
        description=question,
        title=unicode(idx),
        vocabulary=vocabulary,
        required=True,
    )
    return field


def make_multi_field(idx, question, *choices):
    vocabulary = SimpleVocabulary([
        SimpleTerm(title=c, token='%s-%s' % (idx, n), value=c)
        for n, c in enumerate(choices)
    ])
    field = Set(
        __name__='extra_question%s' % idx,
        description=question,
        title=unicode(idx),
        value_type=Choice(vocabulary=vocabulary),
        required=True,
    )
    return field


QTYPES = {
    "choice": make_choice_field,
    "multi": make_multi_field,
    "bool": make_boolean_field,
}


def parse_extra_question_syntax(question):
    sep = "=>"
    exp = [e.strip() for e in re.split(sep, question, 1)]
    label = exp[0]
    if len(exp) == 1:
        elements = ['bool']
    else:
        sep = "::"
        elements = [e.strip() for e in re.split(sep, exp[1])]
        if len(elements) < 2:
            if elements[0] != 'bool':
                raise NotImplementedError(
                    u"Question %r doesn't have any possible values" % label)
    return label, elements[0], elements[1:]


def parse_extra_question(idx, question):
    """examples:
    To be or not to be ? => enum::Yes::Maybe::Never !!::Go and Die!
    What do you like ? => multi::Movies::Sport::Music::Work::Reading
    Is it True ?
    Will you come ? => bool
    """
    label, qtype, values = parse_extra_question_syntax(question)
    factory = QTYPES.get(qtype)
    if factory is None:
        raise NotImplementedError(u"Unknown field %s" % qtype)
    return factory(idx, label, *values)


def generate_extra_questions(text):
    fields = []
    questions = text.strip().split('\n')
    for idx, question in enumerate(questions, 1):
        if not isinstance(question, unicode):
            question = question.decode('utf-8').strip()
        else:
            question = question.strip()
        extra_field = parse_extra_question(idx, question)
        fields.append(extra_field)
    return fields
