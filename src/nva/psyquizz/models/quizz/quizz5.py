# -*- coding: utf-8 -*-

import os
import csv
from nva.psyquizz import Base
from nva.psyquizz.models import FBGU, IQuizz
from nva.psyquizz.models.quizz import QuizzBase

from collections import OrderedDict
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text
from grokcore.component import global_utility
from zope.interface import Interface, implementer
from zope import schema
from zope.component.hooks import getSite
from sqlalchemy.orm import relationship, backref


class IScale1(Interface):

    question1 = schema.Choice(
        title=u"1",
        description=u"Bei meiner Arbeit ist man an Arbeitsvorgängen von Anfang bis Ende beteiligt.",
        vocabulary=FBGU,
        required=True,
    )

    question2 = schema.Choice(
        title=u"2",
        description=u"Bei meiner Arbeit führt man nicht nur kleine Teilaufgaben aus, sondern stellt vollständige Produkte und Dienstleistungen her.",
        vocabulary=FBGU,
        required=True,
    )

    question3 = schema.Choice(
        title=u"3",
        description=u"Man muss vorgegebene Arbeiten nicht nur ausführen, sondern auch selbst planen und die Ergebnisse überprüfen.",
        vocabulary=FBGU,
        required=True,
    )


class IScale2(Interface):

    question4 = schema.Choice(
        title=u"4",
        description=u"Bei meiner Arbeit kann man die Reihenfolge der Aufgabenerledigung selbst bestimmen.",
        vocabulary=FBGU,
        required=True,
    )

    question5 = schema.Choice(
        title=u"5",
        description=u"Man kann bei meiner Arbeit selbst bestimmen, wann man was macht.",
        vocabulary=FBGU,
        required=True,
    )

    question6 = schema.Choice(
        title=u"6",
        description=u"Man hat viele Freiheiten in der Art und Weise, wie man seine Arbeit verrichtet.",
        vocabulary=FBGU,
        required=True,
    )


class IScale3(Interface):

    question7 = schema.Choice(
        title=u"7",
        description=u"Bei meiner Arbeit hat man fast jeden Tag etwas anderes zu tun.",
        vocabulary=FBGU,
        required=True,
    )

    question8 = schema.Choice(
        title=u"8",
        description=u"Die Arbeitsaufgaben wechseln häufig bei meiner Arbeit.",
        vocabulary=FBGU,
        required=True,
    )

    question9 = schema.Choice(
        title=u"9",
        description=u"Man muss bei meiner Arbeit unterschiedliche Fähigkeiten einsetzen.",
        vocabulary=FBGU,
        required=True,
    )


class IScale4(Interface):

    question10 = schema.Choice(
        title=u"10",
        description=u"Man muss viel Energie dafür aufwenden, die für die Arbeit notwendigen Informationen zu beschaffen.",
        vocabulary=FBGU,
        required=True,
    )

    question11 = schema.Choice(
        title=u"11",
        description=u"Erforderliche Unterlagen, Informationen und Daten sind bei meiner Arbeit häufig unvollständig.",
        vocabulary=FBGU,
        required=True,
    )

    question12 = schema.Choice(
        title=u"12",
        description=u"Entscheidungen werden erschwert, weil häufig nicht alle notwendigen Informationen vorliegen.",
        vocabulary=FBGU,
        required=True,
    )

class IScale5(Interface):

    question13 = schema.Choice(
        title=u"13",
        description=u"Die tägliche Informationsmenge bei meiner Arbeit ist zu hoch (z.B. Mails, Unternehmenskommunikation).",
        vocabulary=FBGU,
        required=True,
    )

    question14 = schema.Choice(
        title=u"14",
        description=u"Daten sind häufig zu umfangreich oder zu unstrukturiert, um die wichtigen Informationen zu erkennen.", vocabulary=FBGU,
        required=True,
    )

    question15 = schema.Choice(
        title=u"15",
        description=u"Die vielen unterschiedlichen Informationskanäle (z.B. Akten, Datenbanken, Intranet) sind schwer zu handhaben.",
        vocabulary=FBGU,
        required=True,
    )


class IScale6(Interface):

    question16 = schema.Choice(
        title=u"16",
        description=u"Man weiß nicht genau, wie weit die eigenen Entscheidungsbefugnisse reichen.",
        vocabulary=FBGU,
        required=True,
    )

    question17 = schema.Choice(
        title=u"17",
        description=u"Ich erhalte häufig widersprüchliche Anweisungen von unterschiedlichen Stellen (Führungskräften/Abteilungen).",
        vocabulary=FBGU,
        required=True,
    )

    question18 = schema.Choice(
        title=u"18",
        description=u"Bei meiner Arbeit sind die Prioritäten unklar.",
        vocabulary=FBGU,
        required=True,
    )

class IScale7(Interface):

    question19 = schema.Choice(
        title=u"19",
        description=u"Man muss Aufgaben übernehmen, für die man eigentlich zu wenig eingearbeitet ist.",
        vocabulary=FBGU,
        required=True,
    )

    question20 = schema.Choice(
        title=u"20",
        description=u"Bei meiner Arbeit muss man Tätigkeiten durchführen, für die man eigentlich nicht vollständig ausgebildet bin.",
        vocabulary=FBGU,
        required=True,
    )

    question21 = schema.Choice(
        title=u"21",
        description=u"Man fühlt sich häufig von den Aufgaben überfordert.",
        vocabulary=FBGU,
        required=True,
    )

class IScale8(Interface):

    question22 = schema.Choice(
        title=u"22",
        description=u"Bei meiner Arbeit hat man keine anspruchsvolle Aufgabe.",
        vocabulary=FBGU,
        required=True,
    )

    question23 = schema.Choice(
        title=u"23",
        description=u"Man denkt häufig, dass man mehr leisten könnte, als von einem gefordert wird.",
        vocabulary=FBGU,
        required=True,
    )

    question24 = schema.Choice(
        title=u"24",
        description=u"Man fühlt sich bei meiner Arbeit häufig unterfordert.",
        vocabulary=FBGU,
        required=True,
    )

class IScale9(Interface):

    question25 = schema.Choice(
        title=u"25",
        description=u"Meine Arbeit bringt einen in stark emotional belastende Situationen (z.B. Trauer, Wut).",
        vocabulary=FBGU,
        required=True,
    )

    question26 = schema.Choice(
        title=u"26",
        description=u"Bei meiner Arbeit ist man häufig mit aggressivem Verhalten oder Übergriffen (z.B. von Kundeninnen/Kunden oder von Klientinnen/Klienten) konfrontiert.",
        vocabulary=FBGU,
        required=True,
    )

    question27 = schema.Choice(
        title=u"27",
        description=u"Es passiert häufig, dass man mit unverschämten Personen oder unangemessenen Verhalten zu tun hat.",
        vocabulary=FBGU,
        required=True,
    )


class IScale10(Interface):

    question28 = schema.Choice(
        title=u"28",
        description=u"Bei meiner Arbeit muss man häufig nach außen hin Gefühle zeigen, die nicht mit meinen eigentlichen Gefühlen übereinstimmen.",
        vocabulary=FBGU,
        required=True,
    )

    question29 = schema.Choice(
        title=u"29",
        description=u"Bei meiner Arbeit muss man häufig seine aktuellen Gefühle verbergen.",
        vocabulary=FBGU,
        required=True,
    )

    question30 = schema.Choice(
        title=u"30",
        description=u"Man muss häufig die eigenen Gefühle den momentanen Gefühlen von Anderen anpassen.",
        vocabulary=FBGU,
        required=True,
    )


class IScale11(Interface):

    question31 = schema.Choice(
        title=u"31",
        description=u"Man hat sehr stark variierende Arbeitszeiten.",
        vocabulary=FBGU,
        required=True,
    )

    question32 = schema.Choice(
        title=u"32",
        description=u"Man muss zu ungünstigen Arbeitszeiten arbeiten.",
        vocabulary=FBGU,
        required=True,
    )

    question33 = schema.Choice(
        title=u"33",
        description=u"Bei meiner Arbeit ist man mit schlecht gestalteten Arbeitszeiten / schlecht gestalteter Schichtarbeit konfrontiert.",
        vocabulary=FBGU,
        required=True,
    )


class IScale12(Interface):

    question34 = schema.Choice(
        title=u"34",
        description=u"Bei meiner Arbeit macht man häufig Überstunden.",
        vocabulary=FBGU,
        required=True,
    )

    question35 = schema.Choice(
        title=u"35",
        description=u"Man bekommt häufig kurzfristig zusätzliche Aufgaben, so dass man den Feierabend nicht einhalten kann.",
        vocabulary=FBGU,
        required=True,
    )

    question36 = schema.Choice(
        title=u"36",
        description=u"Auch außerhalb der regulären Arbeitszeiten ist es bei meiner Arbeit häufig erforderlich, verfügbar zu sein.",
        vocabulary=FBGU,
        required=True,
    )



class IScale13(Interface):

    question37 = schema.Choice(
        title=u"37",
        description=u"Um die Arbeitsmenge bei meiner Arbeit zu schaffen, muss man länger arbeiten oder Pausen wegfallen lassen.",
        vocabulary=FBGU,
        required=True,
    )

    question38 = schema.Choice(
        title=u"38",
        description=u"Aufgrund der hohen Arbeitsmenge kommt es häufig zu hohem Zeitdruck.",
        vocabulary=FBGU,
        required=True,
    )

    question39 = schema.Choice(
        title=u"39",
        description=u"Es kommt häufig vor, dass man nicht genügend Zeit hat, alle Aufgaben zu erledigen.",
        vocabulary=FBGU,
        required=True,
    )




class IScale14(Interface):

    question40 = schema.Choice(
        title=u"40",
        description=u"Man wird bei seiner täglichen Arbeit immer wieder durch andere Personen unterbrochen.",
        vocabulary=FBGU,
        required=True,
    )

    question41 = schema.Choice(
        title=u"41",
        description=u"Man hat häufig mehrere Aufgaben gleichzeitig, zwischen denen man hin- und herspringen muss.",
        vocabulary=FBGU,
        required=True,
    )

    question42 = schema.Choice(
        title=u"42",
        description=u"Man muss bei meiner Arbeit häufig aktuelle Arbeiten unterbrechen, weil etwas Wichtiges dazwischenkommt.",
        vocabulary=FBGU,
        required=True,
    )


class IScale15(Interface):

    question43 = schema.Choice(
        title=u"43",
        description=u"Man steht nicht im direktem persönlichen Kontakt mit Kolleginnen und Kollegen.",
        vocabulary=FBGU,
        required=True,
    )

    question44 = schema.Choice(
        title=u"44",
        description=u"An meinem Arbeitsplatz mangelt es an Möglichkeiten zum persönlichen Austausch.",
        vocabulary=FBGU,
        required=True,
    )

    question45 = schema.Choice(
        title=u"45",
        description=u"Man kann sich bei meiner Arbeit nicht mit seinen Kolleginnen und Kollegen unterhalten.",
        vocabulary=FBGU,
        required=True,
    )


class IScale16(Interface):

    question46 = schema.Choice(
        title=u"46",
        description=u"Wenn es Probleme bei der Arbeit gibt, kann man sich auf die Unterstützung der Kolleginnen und Kollegen verlassen.",
        vocabulary=FBGU,
        required=True,
    )

    question47 = schema.Choice(
        title=u"47",
        description=u"Man kann mit seinen Kolleginnen und Kollegen offen über alles reden.",
        vocabulary=FBGU,
        required=True,
    )

    question48 = schema.Choice(
        title=u"48",
        description=u"Meine Kolleginnen und Kollegen sind immer bereit, sich meine Arbeitsprobleme anzuhören.",
        vocabulary=FBGU,
        required=True,
    )


class IScale17(Interface):

    question49 = schema.Choice(
        title=u"49",
        description=u"Es gibt häufig Spannungen unter Kolleginnen und Kollegen.",
        vocabulary=FBGU,
        required=True,
    )

    question50 = schema.Choice(
        title=u"50",
        description=u"Man wird bei meiner Arbeit von anderen über die Maße kritisiert oder bloßgestellt.",
        vocabulary=FBGU,
        required=True,
    )

    question51 = schema.Choice(
        title=u"51",
        description=u"Es gibt häufig Streitereien an meinem Arbeitsplatz.",
        vocabulary=FBGU,
        required=True,
    )


class IScale18(Interface):

    question52 = schema.Choice(
        title=u"52",
        description=u"Meine Führungskraft ist bereit, sich meine Probleme anzuhören.",
        vocabulary=FBGU,
        required=True,
    )

    question53 = schema.Choice(
        title=u"53",
        description=u"Man kann sich auf die Unterstützung der Führungskräfte verlassen, wenn es Probleme bei der Arbeit gibt.",
        vocabulary=FBGU,
        required=True,
    )

    question54 = schema.Choice(
        title=u"54",
        description=u"Meine Führungskraft unterstützt mich, sodass ich meine Aufgaben leichter erfüllen kann.",
        vocabulary=FBGU,
        required=True,
    )


class IScale19(Interface):

    question55 = schema.Choice(
        title=u"55",
        description=u"Man bekommt von Führungskräften sowie von Kolleginnen und Kollegen Rückmeldungen über die Qualität der Arbeit.",
        vocabulary=FBGU,
        required=True,
    )

    question56 = schema.Choice(
        title=u"56",
        description=u"Man erhält Wertschätzung für seine Arbeit.",
        vocabulary=FBGU,
        required=True,
    )

    question57 = schema.Choice(
        title=u"57",
        description=u"Meine Führungskraft gibt mir nützliches Feedback über meine Arbeitsleistung.",
        vocabulary=FBGU,
        required=True,
    )


class IScale20(Interface):

    question58 = schema.Choice(
        title=u"58",
        description=u"Inwieweit sind folgenden Umgebungsbelastungen an Ihrem Arbeitsplatz vorhanden: <br> <br> Lärm",
        vocabulary=FBGU,
        required=True,
    )


class IScale21(Interface):

    question59 = schema.Choice(
        title=u"59",
        description=u"Hitze",
        vocabulary=FBGU,
        required=True,
    )


class IScale22(Interface):

    question60 = schema.Choice(
        title=u"60",
        description=u"Ungünstige Beleuchtung/Blendung",
        vocabulary=FBGU,
        required=True,
    )


class IScale23(Interface):

    question61 = schema.Choice(
        title=u"61",
        description=u"Gefahrstoffe",
        vocabulary=FBGU,
        required=True,
   )


class IScale24(Interface):

    question62 = schema.Choice(
        title=u"62",
        description=u"Räumliche Enge",
        vocabulary=FBGU,
        required=True,
    )


class IScale25(Interface):

    question63 = schema.Choice(
        title=u"63",
        description=u"Ungünstige ergonomische Gestaltung",
        vocabulary=FBGU,
        required=True,
    )


class IScale26(Interface):

    question64 = schema.Choice(
        title=u"64",
        description=u"Ununterbrochene gleiche Bewegung",
        vocabulary=FBGU,
        required=True,
    )


class IScale27(Interface):

    question65 = schema.Choice(
        title=u"65",
        description=u"Unzureichende Gestaltung von Signalen und Hinweisen",
        vocabulary=FBGU,
        required=True,
    )


class IScale28(Interface):

    question66 = schema.Choice(
        title=u"66",
        description=u"Schwere körperliche Arbeit",
        vocabulary=FBGU,
        required=True,
    )


class IScale29(Interface):

    question67 = schema.Choice(
        title=u"67",
        description=u"Fehlende oder ungünstig zu bedienende Arbeitsmittel",
        vocabulary=FBGU,
        required=True,
    )


class IGroupScale(IScale20, IScale21, IScale22, IScale23, IScale24, IScale25, IScale26, IScale27, IScale28, IScale29):
    pass


class IQuizz5(IQuizz, IScale1, IScale2, IScale3, IScale4, IScale5, IScale6, IScale7,
        IScale8, IScale9, IScale10, IScale11, IScale12, IScale13, IScale14, IScale15,
        IScale16, IScale17, IScale18, IScale19, IScale20, IScale21, IScale22, IScale23,
        IScale24, IScale25, IScale26, IScale27, IScale28, IScale29):
    pass


IQuizz5.setTaggedValue("scales", [
    {'iface': IScale1, 'label': u"Vollständigkeit der Aufgabe"},
    {'iface': IScale2, 'label': u"Handlungsspielraum"},
    {'iface': IScale3, 'label': u"Variabilität (Abwechslungsreichtum)"},
    {'iface': IScale4, 'label': u"Informationsmängel"},
    {'iface': IScale5, 'label': u"Informationsüberflutung"},
    {'iface': IScale6, 'label': u"Klarheit der Kompetenzen und Verantwortlichkeiten"},
    {'iface': IScale7, 'label': u"Qualifikationsmängel"},
    {'iface': IScale8, 'label': u"Qualifikationsunterforderung"},
    {'iface': IScale9, 'label': u"Soziale und Emotionale Belastungen"},
    {'iface': IScale10, 'label': u"Emotionsarbeit"},
    {'iface': IScale11, 'label': u"Belastende Arbeitszeit"},
    {'iface': IScale12, 'label': u"Entgrenzte Arbeitszeit"},
    {'iface': IScale13, 'label': u"Zeitdruck/hohe Arbeitsintensität"},
    {'iface': IScale14, 'label': u"Unterbrechungen/Multitasking"},
    {'iface': IScale15, 'label': u"Kommunikation/Kooperation"},
    {'iface': IScale16, 'label': u"Soziale Unterstützung"},
    {'iface': IScale17, 'label': u"Soziale Drucksituationen"},
    {'iface': IScale18, 'label': u"Soziale Unterstützung durch Führungskräfte"},
    {'iface': IScale19, 'label': u"Feedback und Anerkennung"},
#    {'iface': IScale20, 'label': u"Umgebung (Gesamt)"},
    {'iface': IScale20, 'label': u"Lärm"},
    {'iface': IScale21, 'label': u"Hitze"},
    {'iface': IScale22, 'label': u"Ungünstige Beleuchtung"},
    {'iface': IScale23, 'label': u"Gefahrstoffe"},
    {'iface': IScale24, 'label': u"Räumliche Enge"},
    {'iface': IScale25, 'label': u"Ergonomische Gestaltung"},
    {'iface': IScale26, 'label': u"Dauerhaft gleiche Bewegungen"},
    {'iface': IScale27, 'label': u"Gestaltung von Signalen"},
    {'iface': IScale28, 'label': u"Schwere körperliche Arbeit"},
    {'iface': IScale29, 'label': u"Arbeitsmittel"},
])

IQuizz5.setTaggedValue("edit_scales", [
    {'iface': IScale1, 'label': u"Vollständigkeit der Aufgabe", 'translate': True},
    {'iface': IScale2, 'label': u"Handlungsspielraum"},
    {'iface': IScale3, 'label': u"Variabilität (Abwechslungsreichtum)"},
    {'iface': IScale4, 'label': u"Informationsmängel"},
    {'iface': IScale5, 'label': u"Informationsüberflutung", 'translate': True},
    {'iface': IScale6, 'label': u"Klarheit der Kompetenzen und Verantwortlichkeiten"},
    {'iface': IScale7, 'label': u"Qualifikationsmängel"},
    {'iface': IScale8, 'label': u"Qualifikationsunterforderung"},
    {'iface': IScale9, 'label': u"Soziale und Emotionale Belastungen"},
    {'iface': IScale10, 'label': u"Emotionsarbeit"},
    {'iface': IScale11, 'label': u"Belastende Arbeitszeit"},
    {'iface': IScale12, 'label': u"Entgrenzte Arbeitszeit"},
    {'iface': IScale13, 'label': u"Zeitdruck/hohe Arbeitsintensität"},
    {'iface': IScale14, 'label': u"Unterbrechungen/Multitasking"},
    {'iface': IScale15, 'label': u"Kommunikation/Kooperation"},
    {'iface': IScale16, 'label': u"Soziale Unterstützung"},
    {'iface': IScale17, 'label': u"Soziale Drucksituationen"},
    {'iface': IScale18, 'label': u"Soziale Unterstützung durch Führungskräfte"},
    {'iface': IScale19, 'label': u"Feedback und Anerkennung"},
#    {'iface': IScale20, 'label': u"Umgebung (Gesamt)"},
    {'iface': IGroupScale, 'label': u"Umgebung"},
])

IQuizz5.setTaggedValue("averages", OrderedDict((
    (u'Vollständigkeit der Aufgabe', [x[1].title for x in schema.getFieldsInOrder(IScale1)]),
    (u'Handlungsspielraum', [x[1].title for x in schema.getFieldsInOrder(IScale2)]),
    (u'Variabilität (Abwechslungsreichtum)', [x[1].title for x in schema.getFieldsInOrder(IScale3)]),
    (u'Informationsmängel', [x[1].title for x in schema.getFieldsInOrder(IScale4)]),
    (u'Informationsüberflutung', [x[1].title for x in schema.getFieldsInOrder(IScale5)]),
    (u'Klarheit der Kompetenzen und Verantwortlichkeiten', [x[1].title for x in schema.getFieldsInOrder(IScale6)]),
    (u'Qualifikationsmängel', [x[1].title for x in schema.getFieldsInOrder(IScale7)]),
    (u'Qualifikationsunterforderung', [x[1].title for x in schema.getFieldsInOrder(IScale8)]),
    (u'Soziale und Emotionale Belastungen', [x[1].title for x in schema.getFieldsInOrder(IScale9)]),
    (u'Emotionsarbeit', [x[1].title for x in schema.getFieldsInOrder(IScale10)]),
    (u'Belastende Arbeitszeit', [x[1].title for x in schema.getFieldsInOrder(IScale11)]),
    (u'Entgrenzte Arbeitszeiten', [x[1].title for x in schema.getFieldsInOrder(IScale12)]),
    (u'Zeitdruck/hohe Arbeitsintensität', [x[1].title for x in schema.getFieldsInOrder(IScale13)]),
    (u'Unterbrechungen/Multitasking', [x[1].title for x in schema.getFieldsInOrder(IScale14)]),
    (u'Kommunikation/Kooperation', [x[1].title for x in schema.getFieldsInOrder(IScale15)]),
    (u'Soziale Unterstützung', [x[1].title for x in schema.getFieldsInOrder(IScale16)]),
    (u'Soziale Drucksituationen', [x[1].title for x in schema.getFieldsInOrder(IScale17)]),
    (u'Soziale Unterstützung durch Führungskräfte', [x[1].title for x in schema.getFieldsInOrder(IScale18)]),
    (u'Feedback und Anerkennung', [x[1].title for x in schema.getFieldsInOrder(IScale19)]),
#    (u'Umgebung (Gesamt)', [x[1].title for x in schema.getFieldsInOrder(IScale20)]),
    (u'Lärm', [x[1].title for x in schema.getFieldsInOrder(IScale20)]),
    (u'Hitze', [x[1].title for x in schema.getFieldsInOrder(IScale21)]),
    (u'Ungünstige Beleuchtung', [x[1].title for x in schema.getFieldsInOrder(IScale22)]),
    (u'Gefahrenstoffe', [x[1].title for x in schema.getFieldsInOrder(IScale23)]),
    (u'Räumliche Enge', [x[1].title for x in schema.getFieldsInOrder(IScale24)]),
    (u'Ergonomische Gestaltung', [x[1].title for x in schema.getFieldsInOrder(IScale25)]),
    (u'Dauerhaft gleiche Bewegungen', [x[1].title for x in schema.getFieldsInOrder(IScale26)]),
    (u'Gestaltung von Signalen', [x[1].title for x in schema.getFieldsInOrder(IScale27)]),
    (u'Schwere körperliche Arbeit', [x[1].title for x in schema.getFieldsInOrder(IScale28)]),
    (u'Arbeitsmittel', [x[1].title for x in schema.getFieldsInOrder(IScale29)]),
    )))


@implementer(IQuizz5)
class Quizz5(QuizzBase, Base):

    __tablename__ = "quizz5"
    __schema__ = IQuizz5
    __title__ = u"FGBU Fragebogen"
    __base_pdf__ = "fbgu.pdf"
    __supports_diff__ = False

    __table_args__ = {"extend_existing": True}

    id = Column("id", Integer, primary_key=True)

    # Link
    student_id = Column(String, ForeignKey("students.access"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))

    student = relationship(
        "Student",
        cascade="all,delete",
        backref=backref(
            "quizz5", uselist=False, cascade="save-update,delete", single_parent=True
        ),
    )

    # Quizz
    completion_date = Column("completion_date", DateTime)

    question1 = Column("question1", Integer)
    question2 = Column("question2", Integer)
    question3 = Column("question3", Integer)
    question4 = Column("question4", Integer)
    question5 = Column("question5", Integer)
    question6 = Column("question6", Integer)
    question7 = Column("question7", Integer)
    question8 = Column("question8", Integer)
    question9 = Column("question9", Integer)
    question10 = Column("question10", Integer)
    question11 = Column("question11", Integer)
    question12 = Column("question12", Integer)
    question13 = Column("question13", Integer)
    question14 = Column("question14", Integer)
    question15 = Column("question15", Integer)
    question16 = Column("question16", Integer)
    question17 = Column("question17", Integer)
    question18 = Column("question18", Integer)
    question19 = Column("question19", Integer)
    question20 = Column("question20", Integer)
    question21 = Column("question21", Integer)
    question22 = Column("question22", Integer)
    question23 = Column("question23", Integer)
    question24 = Column("question24", Integer)
    question25 = Column("question25", Integer)
    question26 = Column("question26", Integer)
    question27 = Column("question27", Integer)
    question28 = Column("question28", Integer)
    question29 = Column("question29", Integer)
    question30 = Column("question30", Integer)
    question31 = Column("question31", Integer)
    question32 = Column("question32", Integer)
    question33 = Column("question33", Integer)
    question34 = Column("question34", Integer)
    question35 = Column("question35", Integer)
    question36 = Column("question36", Integer)
    question37 = Column("question37", Integer)
    question38 = Column("question38", Integer)
    question39 = Column("question39", Integer)
    question40 = Column("question40", Integer)
    question41 = Column("question41", Integer)
    question42 = Column("question42", Integer)
    question43 = Column("question43", Integer)
    question44 = Column("question44", Integer)
    question45 = Column("question45", Integer)
    question46 = Column("question46", Integer)
    question47 = Column("question47", Integer)
    question48 = Column("question48", Integer)
    question49 = Column("question49", Integer)
    question50 = Column("question50", Integer)
    question51 = Column("question51", Integer)
    question52 = Column("question52", Integer)
    question53 = Column("question53", Integer)
    question54 = Column("question54", Integer)
    question55 = Column("question55", Integer)
    question56 = Column("question56", Integer)
    question57 = Column("question57", Integer)
    question58 = Column("question58", Integer)
    question59 = Column("question59", Integer)
    question60 = Column("question60", Integer)
    question61 = Column("question61", Integer)
    question62 = Column("question62", Integer)
    question63 = Column("question63", Integer)
    question64 = Column("question64", Integer)
    question65 = Column("question65", Integer)
    question66 = Column("question66", Integer)
    question67 = Column("question67", Integer)
    question68 = Column("question68", Integer)
    question69 = Column("question69", Integer)
    question70 = Column("question70", Integer)
    question71 = Column("question71", Integer)
    question72 = Column("question72", Integer)

    extra_questions = Column("extra_questions", Text)

    @staticmethod
    def inverted():
        resources = getSite().configuration.resources
        test = resources.get('strukturangaben.csv')
        with open(test, 'r') as fd:
            def as_float(v):
                return float(v.replace(',', '.'))

            data = csv.reader(fd, delimiter=';')
            next(data)
            for entry in data:
                idx, title, label, tooltip, red, yellow, green, inverted = entry
                yield unicode(title, 'utf-8'), (label, bool(int(inverted)))

    def get_boundaries(self):
        chart_boundaries = IQuizz5.queryTaggedValue("chart_boundaries")
        if chart_boundaries is not None:
            return chart_boundaries
        resources = getSite().configuration.resources
        test = resources.get('strukturangaben.csv')
        with open(test, 'r') as fd:
            def as_float(v):
                return float(v.replace(',', '.'))
            data = csv.reader(fd, delimiter=';')
            next(data)
            boundaries = OrderedDict()
            for entry in data:
                idx, title, label, tooltip, red, yellow, green, inverted = entry
                tooltip = tooltip.decode('utf-8')
                #title = title.decode('utf-8')
                if red.startswith("</="):
                    red = red[3:]
                elif red.startswith(">") or red.startswith("<"):
                    red = red[1:]
                if int(inverted) == 0:
                    boundary = (
                        (as_float(red), '#62B645'),
                        (as_float(yellow), '#FFCC00'),
                        (5, '#D8262B'),
                        unicode(label, 'utf-8'), tooltip, inverted
                    )
                    print "%s; %s; | %s | %s | I0 | R %s | Y %s | G5  --> %s " %(idx, red, yellow, green, boundary[0][0], boundary[1][0], title)
                else:
                    boundary = (
                        (as_float(red), '#D8262B'),
                        (as_float(yellow), '#FFCC00'),
                        (as_float(green), '#62B645'),
                        unicode(label, 'utf-8'), tooltip, inverted
                    )
                    print "%s; %s; | %s | %s | I1 | G %s | Y %s | R5  --> %s " %(idx, red, yellow, green, boundary[0][0], boundary[1][0], title)
                boundaries[unicode(title, 'utf-8')] = boundary
        IQuizz5.setTaggedValue("chart_boundaries", boundaries)
        return boundaries


global_utility(Quizz5, provides=IQuizz, name="quizz5", direct=True)
