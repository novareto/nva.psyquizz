# -*- coding: utf-8 -*-

import os
from zope import schema
from zope.interface import invariant, Invalid, Interface
from zope.location import ILocation
from zope.schema import ValidationError
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from grokcore.component import provider
from uvc.content.interfaces import IContent
from uvc.validation.validation import validateZahl
from uvclight.form_components.fields import OrderedChoices
from nva.psyquizz.i18n import _
from nva.psyquizz.models.quizz.corona_set import (
    ICoronaQuestions, IHomeOfficeQuestions)
from . import deferred_vocabularies
from ..extra_questions import generate_extra_questions


class VKontaktdaten(ValidationError):
    u""" Bitte geben Sie einen Ansprechpartner an oder löschen Sie die Zeile Ansprechpartner und Kontaktdaten."""

def v_about(value):
    if value:
        if '<span> A n s p r e c h p a r t n e r   &nbsp;    und   &nbsp;     K o n t a k t d a t e n </span>' in value:
            raise VKontaktdaten(value)
    return True


ABOUT_TEXT = u"""
<p>Liebe Kolleginnen und Kollegen,</p>
<p> herzlich Willkommen zu unserer Befragung „Gemeinsam zu gesunden Arbeitsbedingungen“! </p>
<p>Bitte beantworten Sie alle Fragen des Fragebogens.
Beim Beantworten der Fragen kann es hilfreich sein, nicht zu lange über die einzelnen Fragen
nachzudenken. Meist ist der erste Eindruck auch der treffendste.</p>
<p>Wir möchten nochmal darauf hinweisen, dass Ihre Angaben absolut vertraulich behandelt werden. Ein Rückschluss auf einzelne Personen wird nicht möglich sein.</p>
<p>Sollten Sie Fragen oder Anmerkungen haben, wenden Sie sich bitte an:</p>
 <p>   <span> A n s p r e c h p a r t n e r   &nbsp;    und   &nbsp     K o n t a k t d a t e n </span> </p>
<p>Wir freuen uns auf Ihre Rückmeldungen!</p>
"""


def deferred(name):
    @provider(IContextSourceBinder)
    def vocabulary(context):
        return deferred_vocabularies[name](context)
    return vocabulary


class MySimpleTerm(SimpleTerm):

    def __init__(self, value, token=None, title=None, iface=None):
        super(MySimpleTerm, self).__init__(value, token, title)
        self.iface = iface



@provider(IContextSourceBinder)
def source_fixed_extra_questions(context):
    rc = [MySimpleTerm('1', '1', u'Corona', ICoronaQuestions), MySimpleTerm('2', '2', u'Homeoffice', IHomeOfficeQuestions)]
    #rc = [MySimpleTerm('2', '2', u'Homeoffice', IHomeOfficeQuestions),]
    return SimpleVocabulary(rc)

deferred_vocabularies['fixed_extra_questions'] = source_fixed_extra_questions


@provider(IContextSourceBinder)
def vocab_type(context):
    rc = [SimpleTerm('1', '1', u'Energieversorgungsunternehmen'),
          SimpleTerm('2', '2', u'Betriebe der Gas-, Fernwärme- und Wasserversorgung sowie Abwasserentsorgung'),
          SimpleTerm('3', '3', u'Betriebe für elektrotechnische, feinmechanische und augenoptische Erzeugnisse'),
          SimpleTerm('4', '4', u'Mess-, Informations- und Medizintechnik'),
          SimpleTerm('5', '5', u'Luft- und Raumfahrzeugtechnik'),
          SimpleTerm('6', '6', u'Elektroinstallationsbetriebe'),
          SimpleTerm('7', '7', u'Graveure, Goldschmiede, Uhrmacher'),
          SimpleTerm('8', '8', u'Herstellung und Bearbeitung von Textilien, Bekleidung, Wäsche'),
          SimpleTerm('9', '9', u'Herstellung von Schuhen'),
          SimpleTerm('10', '10', u'Offset-, Sieb-, Tief- und Digitaldruck'),
          SimpleTerm('11', '11', u'Grafik und Druckvorstufe'),
          SimpleTerm('12', '12', u'Herstellung von Wellpappe, Kartonagen'),
          SimpleTerm('13', '13', u'Papierverarbeitung'),
          SimpleTerm('14', '14', u'Fotografie und Bildjournalismus'),
          SimpleTerm('15', '15', u'sonstige'),
          ]
    return SimpleVocabulary(rc)


@provider(IContextSourceBinder)
def vocab_employees(context):
    rc = [SimpleTerm('1', '1', u'Weniger als 10'),
          SimpleTerm('2', '2', u'Zwischen 10 und 50'),
          SimpleTerm('3', '3', u'Zwischen 51 und 250'),
          SimpleTerm('4', '4', u'Zwischen 251 und 500'),
          SimpleTerm('5', '5', u'Mehr als 500')
          ]
    return SimpleVocabulary(rc)


deferred_vocabularies['type'] = vocab_type
deferred_vocabularies['employees'] = vocab_employees


@provider(IContextSourceBinder)
def exp_db(context):
    rc = [SimpleTerm('true', 'true', u'ja, ich stimme zu'),
          SimpleTerm('false', 'false', u'nein, ich stimme einer anonymisierten \
              Erfassung meiner Umfrageergebnisse nicht zu'),
          ]
    return SimpleVocabulary(rc)



class IQuizz(Interface):
    pass


class IQuizzSecurity(Interface):

    def check(name, quizz, context):
        pass


class ICriterias(IContent):
    pass


class ICriteria(IContent):

    title = schema.TextLine(
        title=_(u"Oberbegriff"),
        #description=_(u"Description Label"),
        description=_(u"Bitte geben Sie hier den Oberbegriff für Ihre Auswertungsgruppen an."),
        required=True,
    )

    items = schema.Text(
        description=_(u'Bitte geben Sie jede Auswertungsgruppe \
                 in eine neue Zeile ein, indem Sie die Eingabetaste („Return“) betätigen.'),
        title=_(u"Please enter one criteria per line"),
        #description=_(u"Description items"),
        required=True,
    )

    @invariant
    def check_items(data):
        items = data.items
        msg = _(u'Bitte geben Sie mindestens 2 Auswertungsgruppen an. Bitte geben Sie jede Auswertungsgruppe in eine neue Zeile ein, indem Sie die Eingeabetaste ("Return") betätigen.')
        if not items:
            raise Invalid(msg)

        clean = [i.strip() for i in items.split('\n') if i.strip()]

        if len(clean) < 2:
            raise Invalid(msg)

        tokens = set((c.lower() for c in clean))
        if len(tokens) != len(clean):
            raise Invalid(_(u"Sie haben zwei identische Werte angegeben."))



class IAccount(ILocation, IContent):

    name = schema.TextLine(
        title=_(u"Fullname"),
        description=_(u"Please give your Fullname here"),
        required=True,
    )

    email = schema.TextLine(
        title=_(u"E-Mail"),
        description=u"Ihre E-Mailadresse benötigen Sie später beim Login.",
        required=True,
    )

    password = schema.Password(
        title=_(u"Password for observation access"),
        description=u"Bitte vergeben Sie ein Passwort (mindestens acht Zeichen).",
        required=True,
    )

    activated = schema.Datetime(
        title=_(u"Active account since"),
        required=False,
    )


class ICompanyTransfer(Interface):

    account_id = schema.Choice(
        title=_(u"Accounts"),
        source=deferred('accounts_choice'),
        required=True,
        )


class ICompanies(Interface):

    company = schema.Choice(
        title=_(u"Company"),
        source=deferred('companies_choice'),
        required=True,
        )


class ICompany(ILocation, IContent):

    name = schema.TextLine(
        title=_(u"Company name"),
        required=True,
    )

    mnr = schema.TextLine(
        title=_(u"Company ID"),
        description=u"Bitte geben Sie hier die ersten acht Stellen Ihrer Mitgliedsnummer bei der BG ETEM ein.",
        required=True,
        constraint=validateZahl,
    )

    courses = schema.Set(
        title=_(u"Courses"),
        required=False,
    )

    exp_db = schema.Choice(
        title=_(u'Forschungsdatenbank'),
        description=u'Ich stimme einer anonymisierten Erfassung meiner Umfrageergebnisse in einer Gesamtdatenbank zu. \
                     Erfasst werden Branche, Anzahl Beschäftigte sowie Ergebnisse der Befragung. \
                     Dies ermöglicht die Ableitung branchenspezifischer Präventionsangebote \
                     sowie die Erstellung von Referenzwerten.',
        required=True,
        source=exp_db
    )

    employees = schema.Choice(
        title=_(u'Employees'),
        description=_(u'Employees_desc'),
        required=False,
        source=deferred('employees'),
    )

    type = schema.Choice(
        title=_(u'Type'),
        description=_(u'Type_desc'),
        required=False,
        source=deferred('type'),
    )


class IClassSession(ILocation, IContent):

    startdate = schema.Date(
        title=_(u"Start date"),
        description=u"Bitte geben Sie an, ab wann die Befragungsseite für Ihre Beschäftigten zugänglich sein soll.",
        required=True,
        )

    enddate = schema.Date(
        title=_(u"Ende der Befragung"),
        required=True,
        )

    students = schema.Set(
        title=_(u"Students"),
        required=False,
        )

    about = schema.Text(
        title=_(u'Einführungstext'),
        description=_("This Text gives Information about the Course to Participants"),
        required=False,
        default=ABOUT_TEXT,
        constraint=v_about,
        )

    #@invariant
    #def check_date(data):
    #    date = data.startdate
    #    if date is not None and date < datetime.date.today():
    #        raise Invalid(_(u"You can't set a date in the past."))


class ICourse(ILocation, IContent):

    name = schema.TextLine(
        title=_(u"Course name"),
        description=(
            u"Bitte geben Sie Ihrer Befragung eine eindeutige "
            u"Bezeichnung wie z.B. Beurteilung Psychischer "
            u"Belastung – Gesamtbetrieb"),
        required=True,
    )

    quizz_type = schema.Choice(
        title=_(u"Quizz"),
        description=_(u" Sie haben bei dem FGBU die Möglichkeit die Fragen innerhalb der Befragung auch auf Englisch darstellen zu lassen. Bitte beachten Sie dazu aber die folgenden Hinweise! <a href='' class='' data-toggle='modal' data-target='#myHelpTranslation'> <span class='glyphicon glyphicon-question-sign' aria-hidden='true'></span> </a>"),
        source=deferred('quizz_choice'),
        required=True,
        default=os.environ.get('DEFAULT_QUIZZ', None),
    )

    fixed_extra_questions = schema.Set(
        title=_(u"Zusatzfragen auswählen"),
        description=_(u"Hier können Sie vordefinierte Zusatzfragen zu Ihrer Befragung auswählen.  <a href='' class='' data-toggle='modal' data-target='#myHelpModal'> <span class='glyphicon glyphicon-question-sign' aria-hidden='true'></span> </a>"),
        required=False,
        value_type=schema.Choice(title=u'Please select one', source=deferred('fixed_extra_questions'))
    )

    extra_questions = schema.Text(
        title=_(u"Eigene Zusatzfragen erstellen"),
        description=_(u"Type your questions : one per line."),
        required=False,
        default=u"",
    )

    criterias = OrderedChoices(
        title=_(u"Auswertungsgruppen festlegen"),
        description=(
            u"Sie können die Reihenfolge der Abfrage im „Fragebogen“ "
            u"verändern, indem Sie die Auswertungsgruppen im rechten "
            u"Kasten nach oben oder unten verschieben. "
            u"Nicht benötigte Auswertungsgruppen verschieben "
            u"Sie in den linken Kasten."),
        value_type=schema.Choice(source=deferred('criterias_choice')),
        required=False,
    )

    @invariant
    def check_extra_questions(data):
        extra_questions = getattr(data, 'extra_questions', None)
        if extra_questions:
            try:
                generate_extra_questions(extra_questions)
            except NotImplementedError:
                raise Invalid('Invalid syntax')


class ICourseSession(IClassSession, ICourse):
    pass


class IStudent(ILocation, IContent):

    access = schema.TextLine(
        title=u"Access string",
        required=True,
    )

    email = schema.TextLine(
        title=u"Email",
        required=True,
    )
