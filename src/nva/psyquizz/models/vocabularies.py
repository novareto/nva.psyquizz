# -*- coding: utf-8 -*-

from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


TrueOrFalse = SimpleVocabulary([
    SimpleTerm(value=True,
               title='eher Ja'),
    SimpleTerm(value=False,
               title='eher Nein'),
    ])


LessToMore = SimpleVocabulary([
    SimpleTerm(value=1,
               title='sehr wenig'),
    SimpleTerm(value=2,
               title='ziemlich wenig'),
    SimpleTerm(value=3,
               title='etwas'),
    SimpleTerm(value=4,
               title='ziemlich viel'),
    SimpleTerm(value=5,
               title='sehr viel'),
    ])


MoreToLessN = SimpleVocabulary([
    SimpleTerm(value=5,
               title=u'trifft gar nicht zu'),
    SimpleTerm(value=4,
               title=u'trifft wenig zu'),
    SimpleTerm(value=3,
               title=u'trifft mittelmäßig zu'),
    SimpleTerm(value=2,
               title=u'trifft überwiegend zu'),
    SimpleTerm(value=1,
               title=u'trifft völlig zu'),
    ])

MoreToLess = SimpleVocabulary([
    SimpleTerm(value=1,
               title=u'trifft gar nicht zu'),
    SimpleTerm(value=2,
               title=u'trifft wenig zu'),
    SimpleTerm(value=3,
               title=u'trifft mittelmäßig zu'),
    SimpleTerm(value=4,
               title=u'trifft überwiegend zu'),
    SimpleTerm(value=5,
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
