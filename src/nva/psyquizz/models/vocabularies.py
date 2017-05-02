# -*- coding: utf-8 -*-

import base64
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


def tokenize(uni):
    return base64.b64encode(uni.encode('utf-8'))


TrueOrFalse = SimpleVocabulary([
    SimpleTerm(value=True,
               token=tokenize(u'eher Ja'),
               title='eher Ja'),
    SimpleTerm(value=False,
               token=tokenize(u'eher Nein'),
               title='eher Nein'),
    ])


LessToMore = SimpleVocabulary([
    SimpleTerm(value=1,
               token=tokenize(u'sehr wenig'),
               title='sehr wenig'),
    SimpleTerm(value=2,
               token=tokenize(u'ziemlich wenig'),
               title='ziemlich wenig'),
    SimpleTerm(value=3,
               token=tokenize(u'etwas'),
               title='etwas'),
    SimpleTerm(value=4,
               token=tokenize(u'ziemlich viel'),
               title='ziemlich viel'),
    SimpleTerm(value=5,
               token=tokenize(u'sehr viel'),
               title='sehr viel'),
    ])


MoreToLessN = SimpleVocabulary([
    SimpleTerm(value=5,
               token=tokenize(u'trifft gar nicht zu'),
               title=u'trifft gar nicht zu'),
    SimpleTerm(value=4,
               token=tokenize(u'trifft wenig zu'),
               title=u'trifft wenig zu'),
    SimpleTerm(value=3,
               token=tokenize(u'trifft mittelmäßig zu'),
               title=u'trifft mittelmäßig zu'),
    SimpleTerm(value=2,
               token=tokenize(u'trifft überwiegend zu'),
               title=u'trifft überwiegend zu'),
    SimpleTerm(value=1,
               token=tokenize(u'trifft völlig zu'),
               title=u'trifft völlig zu'),
    ])

MoreToLess = SimpleVocabulary([
    SimpleTerm(value=1,
               token=tokenize(u'trifft gar nicht zu'),
               title=u'trifft gar nicht zu'),
    SimpleTerm(value=2,
               token=tokenize(u'trifft wenig zu'),
               title=u'trifft wenig zu'),
    SimpleTerm(value=3,
               token=tokenize(u'trifft mittelmäßig zu'),
               title=u'trifft mittelmäßig zu'),
    SimpleTerm(value=4,
               token=tokenize(u'trifft überwiegend zu'),
               title=u'trifft überwiegend zu'),
    SimpleTerm(value=5,
               token=tokenize(u'trifft völlig zu'),
               title=u'trifft völlig zu'),
    ])


durations = SimpleVocabulary([
    SimpleTerm(value=21,
               title=u'3 Wochen'),
    SimpleTerm(value=28,
               title=u'4 Wochen'),
    SimpleTerm(value=35,
               title=u'5 Wochen'),
    ])
