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


AF = SimpleVocabulary([
    SimpleTerm(value=0,
               title=u'0 - Völlig arbeitsunfähig'),
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


GOODBAD = SimpleVocabulary([
    SimpleTerm(value=5,
               title=u'Sehr gut'),
    SimpleTerm(value=4,
               title=u'Eher gut'),
    SimpleTerm(value=3,
               title=u'Mittelmäßig'),
    SimpleTerm(value=2,
               title=u'Eher schlecht'),
    SimpleTerm(value=1,
               title=u'Sehr schlecht'),
    ])


TIMESPAN = SimpleVocabulary([
    SimpleTerm(value=5,
               title=u'Überhaupt keinen'),
    SimpleTerm(value=4,
               title=u'Höchstens 9 Tage'),
    SimpleTerm(value=3,
               title=u'10 - 24 Tage'),
    SimpleTerm(value=2,
               title=u'25 - 99 Tage'),
    SimpleTerm(value=1,
               title=u'100 - 365 Tage'),
    ])


ASSESMENT = SimpleVocabulary([
    SimpleTerm(value=1,
               title=u'Unwahrscheinlich'),
    SimpleTerm(value=4,
               title=u'Nicht sicher'),
    SimpleTerm(value=7,
               title=u'Ziemlich sicher'),
    ])


FREQUENCY = SimpleVocabulary([
    SimpleTerm(value=4,
               title=u'Ständig'),
    SimpleTerm(value=3,
               title=u'Eher häufig'),
    SimpleTerm(value=2,
               title=u'Manchmal'),
    SimpleTerm(value=1,
               title=u'Eher selten'),
    SimpleTerm(value=0,
               title=u'Niemals'),
    ])
