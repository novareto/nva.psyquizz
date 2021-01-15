
# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.schema import Choice
from nva.psyquizz.models.vocabularies import make_vocabulary 
from zope.schema.vocabulary import SimpleTerm


FREQUENCY = make_vocabulary('frequency_corona', [
    SimpleTerm(value=u'trifft gar nicht zu',
               title=u'trifft gar nicht zu'),
    SimpleTerm(value=u'trifft wenig zu',
               title=u'trifft wenig zu'),
    SimpleTerm(value=u'trifft mittelmäßig zu',
               title=u'trifft mittelmäßig zu'),
    SimpleTerm(value=u'trifft überwiegend zu',
               title=u'trifft überwiegend zu'),
    SimpleTerm(value=u'trifft völlig zu',
               title=u'trifft völlig zu'),
    ])


class ICoronaQuestions(Interface):
    """ Corona Fragen """

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

    extra_six = Choice(
        title=u"6",
        description=u"Mein Betrieb unterstützt mich im Umgang mit den Zusatzbelastungen durch Corona (z.B. Schließung von Schulen oder Kitas).",
        source=FREQUENCY
    )

    extra_seven = Choice(
        title=u"7",
        description=u"Durch Corona hat sich meine Arbeitszeit (Lage, Dauer) negativ verändert.",
        source=FREQUENCY
    )


class IHomeOfficeQuestions(Interface):
    """ Home Office """

    extra_ho_one = Choice(
        title=u"1",
        description=u"Ich kann im Homeoffice ungestört arbeiten.",
        source=FREQUENCY
    )

    extra_ho_two = Choice(
        title=u"2",
        description=u"Im Homeoffice ist mein Arbeitsplatz für mich passend gestaltet (Stuhl, Tisch, Bildschirm etc.).",
        source=FREQUENCY
    )

    extra_ho_three = Choice(
        title=u"3",
        description=u"Im Homeoffice ist meine technische Ausstattung gut (Software, Hardware, Internetverbindung etc.).",
        source=FREQUENCY
    )

    extra_ho_four = Choice(
        title=u"4",
        description=u"Der Austausch mit meinen Kolleginnen und Kollegen funktioniert aus dem Homeoffice heraus gut.",
        source=FREQUENCY
    )

    extra_ho_five = Choice(
        title=u"5",
        description=u"Meine Erreichbarkeitszeiten im Homeoffice sind mit meiner Führungskraft und meinem Team abgestimmt.",
        source=FREQUENCY
    )

    extra_ho_six = Choice(
        title=u"6",
        description=u"Ziele und Erwartungen an meine Arbeit im Homeoffice sind mit meiner Führungskraft und Kolleginnen und Kollegen eindeutig geklärt.",
        source=FREQUENCY
    )

    extra_ho_seven = Choice(
        title=u"7",
        description=u"Meine Arbeit im Homeoffice lässt sich gut selbst organisieren.",
        source=FREQUENCY
    )
    extra_ho_eight = Choice(
        title=u"8", 
        description=u"Meine Arbeit im Homeoffice ermöglicht es mir, Beruf und Privatleben miteinander zu vereinbaren.",
        source=FREQUENCY
    )
