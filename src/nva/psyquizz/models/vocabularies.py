# -*- coding: utf-8 -*-

import base64
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


def tokenize(uni):
    return base64.b64encode(uni.encode('utf-8'))


def make_vocabulary(name, terms):
     vocabulary = SimpleVocabulary(terms)
     vocabulary.__name__ = name
     return vocabulary


TrueOrFalse = make_vocabulary('True or false', [
    SimpleTerm(value=True,
               token=tokenize(u'eher Ja'),
               title='eher Ja'),
    SimpleTerm(value=False,
               token=tokenize(u'eher Nein'),
               title='eher Nein'),
    ])


LessToMore = make_vocabulary('Less to more', [
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


MoreToLessN = make_vocabulary('More to less N', [
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

MoreToLess = make_vocabulary('More to less', [
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


durations = make_vocabulary('durations', [
    SimpleTerm(value=21,
               title=u'3 Wochen'),
    SimpleTerm(value=28,
               title=u'4 Wochen'),
    SimpleTerm(value=35,
               title=u'5 Wochen'),
    ])


AF = make_vocabulary('AF', [
    SimpleTerm(value=0,
               title=u'0 - völlig arbeitsunfähig'),
    SimpleTerm(value=1,
               title=u'1'),
    SimpleTerm(value=2,
               title=u'2'),
    SimpleTerm(value=3,
               title=u'3'),
    SimpleTerm(value=4,
               title=u'4'),
    SimpleTerm(value=5,
               title=u'5'),
    SimpleTerm(value=6,
               title=u'6'),
    SimpleTerm(value=7,
               title=u'7'),
    SimpleTerm(value=8,
               title=u'8'),
    SimpleTerm(value=9,
               title=u'9'),
    SimpleTerm(value=10,
               title=u'10 - derzeit die beste Arbeitsfähigkeit'),
    ])


GOODBAD = make_vocabulary('good or bad', [
    SimpleTerm(value=5,
               title=u'sehr gut'),
    SimpleTerm(value=4,
               title=u'eher gut'),
    SimpleTerm(value=3,
               title=u'mittelmäßig'),
    SimpleTerm(value=2,
               title=u'eher schlecht'),
    SimpleTerm(value=1,
               title=u'sehr schlecht'),
    ])


TIMESPAN = make_vocabulary('timespan', [
    SimpleTerm(value=5,
               title=u'überhaupt keinen'),
    SimpleTerm(value=4,
               title=u'höchstens 9 Tage'),
    SimpleTerm(value=3,
               title=u'10 bis 24 Tage'),
    SimpleTerm(value=2,
               title=u'25 bis 99 Tage'),
    SimpleTerm(value=1,
               title=u'100 bis 365 Tage'),
    ])


ASSESMENT = make_vocabulary('assesment', [
    SimpleTerm(value=1,
               title=u'unwahrscheinlich'),
    SimpleTerm(value=4,
               title=u'nicht sicher'),
    SimpleTerm(value=7,
               title=u'ziemlich sicher'),
    ])


FREQUENCY = make_vocabulary('frequency', [
    SimpleTerm(value=4,
               title=u'häufig'),
    SimpleTerm(value=3,
               title=u'eher häufig'),
    SimpleTerm(value=2,
               title=u'manchmal'),
    SimpleTerm(value=1,
               title=u'eher selten'),
    SimpleTerm(value=0,
               title=u'niemals'),
    ])

FREQUENCY1 = make_vocabulary('frequency1', [
    SimpleTerm(value=4,
               title=u'immer'),
    SimpleTerm(value=3,
               title=u'eher häufig'),
    SimpleTerm(value=2,
               title=u'manchmal'),
    SimpleTerm(value=1,
               title=u'eher selten'),
    SimpleTerm(value=0,
               title=u'niemals'),
    ])

FREQUENCY2 = make_vocabulary('frequency2', [
    SimpleTerm(value=4,
               title=u'ständig'),
    SimpleTerm(value=3,
               title=u'eher häufig'),
    SimpleTerm(value=2,
               title=u'manchmal'),
    SimpleTerm(value=1,
               title=u'eher selten'),
    SimpleTerm(value=0,
               title=u'niemals'),
    ])


FBGU = make_vocabulary('fbgu', [
    SimpleTerm(value=1, title=u"Trifft nicht zu"),
    SimpleTerm(value=2, title=u"Trifft eher nicht zu"),
    SimpleTerm(value=3, title=u"Trifft eher zu"),
    SimpleTerm(value=4, title=u"Trifft zu"),
    ])
