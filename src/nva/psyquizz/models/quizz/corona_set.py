
# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import Choice
from nva.psyquizz.models.vocabularies import make_vocabulary 
from zope.schema.vocabulary import SimpleTerm



FREQUENCY = make_vocabulary('frequency_corona', [
    SimpleTerm(value=u'häufig',
               title=u'häufig'),
    SimpleTerm(value=u'eher häufig',
               title=u'eher häufig'),
    SimpleTerm(value=u'manchmal',
               title=u'manchmal'),
    SimpleTerm(value=u'eher selten',
               title=u'eher selten'),
    SimpleTerm(value=u'niemals',
               title=u'niemals'),
    ])



class ICoronaQuestions(Interface):

    extra_one = Choice(
        title=u"1",
        description=u"Durch Corona habe ich zu wenig Arbeit.",
        source=FREQUENCY
    )

    extra_two = Choice(
        title=u"2",
        description=u"Durch Corona habe ich zu wenig Kontakt mit Kolleginnen und Kollegen.",
        source=FREQUENCY
    )

    extra_three = Choice(
        title=u"3",
        description=u"Ich werde über die Corona Maßnahmen im Betrieb ausreichend informiert.",
        source=FREQUENCY
    )

    extra_four = Choice(
        title=u"4",
        description=u"Ich fühle mich durch die Maßnahmen in meinem Betrieb ausreichend geschützt.",
        source=FREQUENCY
    )

    extra_five = Choice(
        title=u"5",
        description=u"Ich habe Angst durch die Pandemie meinen Arbeitsplatz zu verlieren.",
        source=FREQUENCY
    )


class IHomeOfficeQuestions(Interface):

    extra_one = Choice(
        title=u"1",
        description=u"Ich kann im Homeoffice ungestört arbeiten.",
        source=FREQUENCY
    )

    extra_two = Choice(
        title=u"2",
        description=u"Mein Arbeitsplatz ist für mich passend gestaltet (Stuhl, Tisch, Bildschirm etc.).",
        source=FREQUENCY
    )

    extra_three = Choice(
        title=u"3",
        description=u"Meine technische Ausstattung ist gut (Software, Hardware, Internetverbindung etc.).",
        source=FREQUENCY
    )

    extra_four = Choice(
        title=u"4",
        description=u"Der digitale Austausch mit meinen Kolleginnen und Kollegen funktioniert gut.",
        source=FREQUENCY
    )

    extra_five = Choice(
        title=u"5",
        description=u"Meine Erreichbarkeitszeiten sind mit meiner Führungskraft und meinem Team abgestimmt.",
        source=FREQUENCY
    )

    extra_six = Choice(
        title=u"6",
        description=u"Ziele und Erwartungen an meine Arbeit sind mit meiner Führungskraft und Kolleginnen und Kollegen eindeutig geklärt.",
        source=FREQUENCY
    )

    extra_seven = Choice(
        title=u"7",
        description=u"Meine Arbeit lässt sich gut selbst organisieren.",
        source=FREQUENCY
    )
    extra_eight = Choice(
        title=u"8",
        description=u"Meine Arbeit ermöglicht es mir, Beruf und Privatleben miteinander zu vereinbaren.",
        source=FREQUENCY
    )
