# -*- coding: utf-8 -*-

from uvc.protectionwidgets import Captcha
import os
import json
import uuid
import hashlib
import datetime
import html2text
import uvclight
import re

from .. import wysiwyg, quizzjs, startendpicker
from ..apps.anonymous import QuizzBoard
from ..i18n import _
from ..interfaces import IAnonymousRequest, ICompanyRequest
from ..interfaces import QuizzAlreadyCompleted, QuizzClosed
from ..interfaces import IRegistrationRequest
from ..models import HistoryEntry
from ..models import Account, Company, Course, ClassSession, Student
from ..models import ICourseSession, IAccount, ICompany, ICourse, IClassSession
from ..models import IQuizz, TrueOrFalse
from ..models import Criteria, CriteriaAnswer, ICriteria, ICriterias
from ..models.criterias import criterias_table
from ..models.quizz.quizz4 import IQuizz4
from nva.psyquizz.browser.lib.emailer import SecureMailer, prepare, ENCODING

import grokcore.component as grok
from grokcore.component import Adapter, provides, context, baseclass
from grokcore.component import adapter, adapts, implementer

from cromlech.sqlalchemy import get_session
from dolmen.forms.base import (
    Field, SuccessMarker, makeAdaptiveDataManager, NO_VALUE)
from dolmen.forms.base.actions import Action, Actions
from dolmen.forms.base.errors import Error
from dolmen.forms.base.utils import apply_data_event
from dolmen.forms.crud.actions import message
from dolmen.forms.ztk.widgets.choice import ChoiceField
from dolmen.menu import menuentry, order
from js.jqueryui import jqueryui
from nva.psyquizz import quizzjs
from siguvtheme.resources import all_dates, datepicker_de
from sqlalchemy import func
from string import Template
from uvc.design.canvas import IContextualActionsMenu
from uvc.design.canvas import IDocumentActions
from uvclight import Form, EditForm, DeleteForm, Fields, SUCCESS, FAILURE
from uvclight import action, layer, name, title, get_template
from uvclight.auth import require
from zope.component import getUtility
from zope.interface import Interface, provider
from zope.schema import Bool, List, Int, Choice, Password, TextLine
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from dolmen.forms.base.interfaces import IForm
from cromlech.browser import ITemplate
from ..interfaces import IQuizzLayer
from ..extra_questions import generate_extra_questions
from siguvtheme.uvclight import IDGUVRequest


@adapter(IForm, IQuizzLayer)
@implementer(ITemplate)
def form_quizz_template(context, request):
    """default template for the menu"""
    return uvclight.get_template('form.cpt', __file__)


with open(os.path.join(os.path.dirname(__file__), 'lib', 'mail.tpl'), 'r') as fd:
    data = unicode(fd.read(), 'utf-8')
    mail_template = Template(data.encode(ENCODING))


def send_activation_code(smtp, company_name, email, code, base_url):
    mailer = SecureMailer(smtp)  # BBB
    from_ = 'extranet@bgetem.de'
    title = (u'Gemeinsam zu gesunden Arbeitsbedingungen – Aktivierung').encode(
        ENCODING)
    with mailer as sender:
        html = mail_template.substitute(
            title=title,
            encoding=ENCODING,
            base_url=base_url,
            email=email.encode(ENCODING),
            company=company_name.encode(ENCODING),
            activation_code=code)

        text = html2text.html2text(html.decode('utf-8'))
        mail = prepare(from_, email, title, html, text.encode('utf-8'))
        sender(from_, email, mail.as_string())
    return True


class IExtraQuestions(Interface):
    pass


IExtraQuestions.setTaggedValue('label', 'Extra questions')


class IStudentFilters(Interface):
    pass


IStudentFilters.setTaggedValue('label', 'Getting started')


@provider(IContextSourceBinder)
def get_strategy(context):
    return SimpleVocabulary((
        SimpleTerm('fixed', 'fixed', u'Zugang mit Kennwort'),
       # SimpleTerm('mixed', 'mixed', u'Feste und freie Anzahl von Teilnehmern'),
        SimpleTerm('free', 'free', u'Offener Zugang'),
    ))


class IPopulateCourse(Interface):

    strategy = Choice(
        title=u"Zugang zur Befragung",
        description=_(u"Geben Sie an, wie der Zugang der Beschäftigten zum \
                      „Fragebogen“ gestaltet sein soll: Offen oder mit \
                      individuellen Kennwort."),
        source=get_strategy,
    )

    nb_students = Int(
        title=_(u"Number of students"),
        description=u"Für jeden der Teilnehmer wird ein Kennwort angelegt.\
        Legen Sie im Zweifelsfall einige Teilnehmer zu viel als\
        „Sicherheitsreserve“ an, falls z.B. Teilnehmer ihr Kennwort verlieren.",
        required=False,
        )

    p2p = Bool(
        title=u"Paper2Disk",
        description=_(u"Sollen einzelne Beschäftigte mit Papierfragebogen \
                        anstatt auf elektronischen Weg teilnehmen?")
        )


class PreviewExtraQuestions(Form):
    baseclass()

    actions = Actions()
    ignoreRequest = True
    ignoreContent = True

    def __init__(self, context, request, text):
        Form.__init__(self, context, request)
        extra_fields = generate_extra_questions(text)
        self.fields = Fields(*extra_fields)
        for field in self.fields:
            if isinstance(field, Choice):
                field.mode = 'radio'

    @property
    def action(self):
        return ''

    def render(self):
        preview = u'''<div id="extra_questions_preview"> KLAUS KLAUS %s</div>'''
        widgets = ['''<div> Vorschau - So wird die Frage nach der
                Auswertungsgruppe im Fragebogen dargestellt: <br> <br>  %s</div>''' % widget.render()
                   for widget in self.fieldWidgets]
        return preview % '\n'.join(widgets)


class ExtraQuestions(uvclight.View):
    context(Interface)
    uvclight.name('preview_extra_questions')
    require('zope.Public')

    def render(self):
        questions = self.request.form.get('extra_questions', None)
        if questions is None:
            return ''
        preview = PreviewExtraQuestions(self.context, self.request, questions)
        preview.updateForm()
        return preview.render()


class PreviewCriterias(Form):
    baseclass()

    actions = Actions()

    def __init__(self, context, request, title, items):
        Form.__init__(self, context, request)
        self.criterias = items
        self.title = title
        self.prefix = 'preview'

    @property
    def action(self):
        return ''

    @property
    def fields(self):
        values = SimpleVocabulary([
            SimpleTerm(value=c.strip(), token=idx, title=c.strip())
            for idx, c in enumerate(self.criterias.split('\n'), 1)
            if c.strip()])

        fields = Fields(Choice(
            __name__='criteria_1',
            title=self.title.decode('utf-8'),
            description=u"Wählen Sie das Zutreffende aus.",
            vocabulary=values,
            required=True,
        ))
        fields['criteria_1'].mode = 'radio'
        return fields

    def render(self):
        field = self.fieldWidgets['preview.field.criteria_1']
        return u"""<div class="preview" style="border: 5px solid #efefef;
    padding: 10px; margin: 5px"><h3>Vorschau</h3> Vorschau - So wird die Frage
    nach der Auswertungsgruppe im Fragebogen dargestellt: <br> <br> <label> %s </label>
    <p> Wählen Sie das zutreffende aus. </p> <br> %s</div>""" % (field.title, field.render())


@menuentry(IContextualActionsMenu, order=10)
class CreateCriterias(Form):
    context(ICriterias)
    name('add.criteria')
    title(_(u'Add a criteria'))
    require('zope.Public')

    fields = Fields(ICriteria).select('title', 'items')
    label = u"Auswertungsgruppen anlegen <a href='' data-toggle='modal' data-target='#myModal'> <span class='glyphicon glyphicon-question-sign' aria-hidden='true'></span> </a>"
    description = u"""
Bitte geben Sie einen Oberbegriff für Ihre Auswertungsgruppen an (z.B.  
„Abteilung“). Zu jedem Oberbegriff gehören mindestens zwei Auswertungsgruppen (z.B.  
„Personalabteilung“ und „Produktion“). <b>Aus Datenschutzgründen werden nur Ergebnisse von Auswertungsgruppen angezeigt, 
von denen mindestens sieben ausgefüllte „Fragebogen“ vorliegen.</b>
"""

    preview = None

    @property
    def action_url(self):
        quizzjs.need()
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('school')
        criteria = Criteria(**data)
        criteria.company_id = self.context.__parent__.id
        session.add(criteria)
        session.flush()
        session.refresh(criteria)
        self.flash(_(u'Criteria added with success.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Vorschau'))
    def handle_preview(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        preview = PreviewCriterias(self.context, self.request, **data)
        preview.updateForm()
        self.preview = preview.render()

    def render(self):
        html = Form.render(self)
        if self.preview:
            html += self.preview
        return html


class EditCriteria(EditForm):
    context(ICriteria)
    name('index')
    title(_(u'Edit criteria'))
    require('zope.Public')
    label = ""

    fields = Fields(ICriteria).select('title', 'items')
    actions = Actions()

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Cancel'))
    def cancel(self):
        message(_(u"Update aborted"))
        url = self.application_url()
        return SuccessMarker('Aborted', True, url=url)

    @action(_(u"Update"))
    def save(self):
        data, errors = self.extractData()
        if errors:
            self.submissionError = errors
            return FAILURE

        apply_data_event(self.fields, self.getContentData(), data)
        message(_(u"Ihre Auswertungsgruppe wurde aktualisiert."))
        url = self.application_url()
        return SuccessMarker('Updated', True, url=url)


class DeletedCriteria(DeleteForm):
    context(ICriteria)
    name('delete')
    title(_(u'Delete'))
    require('zope.Public')

    label = u"Auswertungsgruppe löschen"

    @property
    def description(self):
        return u"Wollen sie die Auswertungsgruppe '%s' wirklich löschen" % (
            self.context.title)

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')

        record = HistoryEntry(
            action=u"Delete",
            type=u"Critera",
            description=u"Delete Criteria %s" % self.context.id)

        session.add(record)
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.application_url())
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class AddSession(Form):
    context(ICourse)
    name('add.session')
    title(_(u'Add a session'))
    require('zope.Public')

    fields = Fields(IPopulateCourse) + Fields(IClassSession).select('startdate', 'enddate', 'about')
    fields['strategy'].mode = "radio"

    def update(self):
        jqueryui.need()
        startendpicker.need()
        wysiwyg.need()
        quizzjs.need()
        Form.update(self)

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('school')
        strategy = dict(
           nb_students=data.pop('nb_students'),
           strategy=data.get('strategy')
        )
        clssession = ClassSession(**data)
        clssession.course_id = self.context.id
        clssession.company_id = self.context.__parent__.id
        session.add(clssession)
        session.flush()
        session.refresh(clssession)
        if strategy.get('strategy') in ('mixed','fixed'):
            if strategy['nb_students'] <= 7:
                self.flash(u'Auswertungen sind erst ab 7 Teilnehmer zulässig. Bitte erhöhen Sie die Anzahl der Teilnehmer auf mindestens 7')
                return FAILURE
            for student in clssession.generate_students(strategy['nb_students']):
                clssession.append(student)
        self.flash(_(u'Session added with success.'))
        self.redirect('%s' % self.application_url())
        return SUCCESS


class ICaptched(Interface):

    captcha = Captcha(
        title=u'Eingabe Sicherheitscode',
        required=True)


class IVerifyPassword(Interface):

    verif = Password(
        title=_(u'Retype password'),
        required=True)


@menuentry(IContextualActionsMenu, order=10)
class CreateAccount(Form):
    name('index')
    layer(IRegistrationRequest)
    title(_(u'Add an account'))
    require('zope.Public')

    dataValidators = []
    fields = (Fields(IAccount).select('name', 'email', 'password') +
              Fields(IVerifyPassword, ICaptched))

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        session = get_session('school')

        if errors:
            return FAILURE

        if not data['password'] == data['verif']:
            self.errors.append(
                Error(identifier='form.field.password',
                      title='Password and verification mismatch'))
            self.errors.append(
                Error(identifier='form.field.verif',
                      title='Password and verification mismatch'))
            self.flash(_(u'Password and verification mismatch.'))
            return FAILURE

        existing = session.query(Account).filter(
            func.lower(Account.email) == data['email'].lower())
        if existing.count():
            self.flash(_(u'User with given email already exists.'))
            self.errors.append(
                Error(
                    identifier='form.field.email',
                    title='Diese E-Mail Adresse existiert bereits im System.'))
            return FAILURE

        # pop the captcha and verif, it's not a needed data
        data.pop('verif')
        if 'captcha' in data:
            data.pop('captcha')

        # hashing the password
        salt = uuid.uuid4().hex
        password = data.pop('password').encode('utf-8')
        data['password'] = hashlib.sha512(password + salt).hexdigest()
        data['salt'] = salt
        if 'ack_form' in data:
            data.pop('ack_form')
        account = Account(**data)
        code = account.activation = str(uuid.uuid1())
        session.add(account)
        session.flush()
        session.refresh(account)

        base_url = self.application_url().replace('/register', '')

        # We send the email.
        send_activation_code(
            self.context.configuration.smtp_server,
            data['name'], data['email'], code, base_url)

        self.flash(_(u'Account added with success.'))
        self.redirect('%s/registered' % self.application_url())
        return SUCCESS


@menuentry(IDocumentActions, order=20)
class DeletedAccount(DeleteForm):
    context(Account)
    name('delete')
    require('manage.company')
    title(_(u'Delete'))

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')

        record = HistoryEntry(
            action=u"Delete",
            type=u"Account",
            description=u"Delete Account %s" % self.context.email)

        session.add(record)
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.url(self.application_url()))
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class CreateCompany(Form):
    name('add.company')
    context(Account)
    layer(ICompanyRequest)
    title(_(u'Add a company'))
    require('manage.company')

    label = u'Betrieb anlegen <a href="" data-toggle="modal" data-target="#myModal"> <span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></a>'

    dataValidators = []
    fields = Fields(ICompany).select(
        'name', 'mnr', 'exp_db', 'type', 'employees')
    fields['mnr'].htmlAttributes = {'maxlength': 8}
    fields['exp_db'].mode = "blockradio"

    def htmlId(self):
        return u"add.course"

    def updateForm(self):
        super(CreateCompany, self).updateForm()
        #self.fieldWidgets.get('form.field.exp_db').template = get_template(
        #    'checkbox.cpt', __file__)
        name = self.fieldWidgets['form.field.name']
        nv = u""
        name.value = {'form.field.name': nv}
        quizzjs.need()

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        session = get_session('school')

        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        # create it
        if not data['exp_db']:
            data.pop('employees')
            data.pop('type')
        company = Company(**data)
        company.account_id = self.context.email
        session.add(company)
        session.flush()
        session.refresh(company)

        # redirect
        base_url = self.url(self.context)
        self.flash(_(u'Company added with success.'))
        self.redirect(base_url)
        return SUCCESS

    @action(_(u'Abbrechen'))
    def handle_cancel(self):
        base_url = self.url(self.context)
        self.redirect(base_url)
        return SUCCESS


@menuentry(IDocumentActions, order=20)
class DeletedCompany(DeleteForm):
    context(Company)
    name('delete')
    require('manage.company')
    title(_(u'Delete'))

    @property
    def label(self):
        return u"Betrieb löschen"

    @property
    def description(self):
        return u"Wollen sie den Betrieb %s wirklich löschen" % self.context.name

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')

        record = HistoryEntry(
            action=u"Delete",
            type=u"Company",
            description=u"Delete Company %s" % self.context.id)

        session.add(record)
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.application_url())
        return SUCCESS


#from uvclight.form_components.widgets import InOutWidget
#from dolmen.forms.ztk.widgets.collection import CollectionSchemaField
#from dolmen.forms.ztk.widgets.choice import ChoiceSchemaField
#from zope.interface import Interface
#
#class InOutWidget(InOutWidget):
#    adapts(CollectionSchemaField, ChoiceSchemaField, Interface, Interface)




@menuentry(IContextualActionsMenu, order=10)
class CreateCourse(Form):
    context(Company)
    name('add.course')
    require('manage.company')
    title(_(u'Add a course'))

    label = u'Befragung anlegen <a href="" data-toggle="modal" data-target="#myModal"> <span class="glyphicon glyphicon-question-sign" aria-hidden="true"></span></a>'
    inline = False

    @property
    def fields(self):
        course_fields = Fields(ICourse).select(
            'name', 'criterias', 'quizz_type', 'extra_questions', 'fixed_extra_questions')
        populate_fields = Fields(IPopulateCourse)
        populate_fields['strategy'].mode = "radio"
        session_fields = Fields(IClassSession).select(
            'startdate', 'enddate', 'about')
        course_fields['extra_questions'].mode = "SpecialInput"
        return course_fields + populate_fields + session_fields

    def update(self):
        #all_dates.need()
        #datepicker_de.need()
        startendpicker.need();
        jqueryui.need()
        wysiwyg.need()
        quizzjs.need()
        Form.update(self)

    def updateForm(self):
        super(CreateCourse, self).updateForm()
        name = self.fieldWidgets['form.field.name']
        nv = u"Beurteilung Psychischer Belastung %s" % (
            datetime.datetime.now().strftime('%Y'))
        courses = len(list(self.context.courses))
        if courses > 0:
            nv = "%s (%s)" % (nv, str(courses + 1))
        name.value = {'form.field.name': nv}
        criterias = self.fieldWidgets['form.field.criterias']
        criterias.value = {
            'form.field.criterias.present': u'1',
            'form.field.criterias': [
                v.token for v in
                criterias.source.vocabularyFactory(self.context)]}

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Add'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            #self.flash(_(u'An error occurred.'))
            return FAILURE
        session = get_session('school')
        csdata = dict(
            startdate=data.pop('startdate'),
            enddate=data.pop('enddate'),
            about=data.pop('about'),
            strategy=data.pop('strategy'),
            p2p=data.pop('p2p')
        )
        strategy = dict(
           nb_students=data.pop('nb_students'),
           strategy=csdata.get('strategy')
        )
        #data['quizz_type'] = "quizz2"
        course = Course(**data)

        course.company_id = self.context.id
        session.add(course)
        session.flush()
        session.refresh(course)
        clssession = ClassSession(**csdata)

        clssession.course_id = course.id
        clssession.company_id = self.context.id
        session.add(clssession)
        session.flush()
        session.refresh(clssession)
        if strategy.get('strategy') in ('mixed','fixed'):
            if strategy['nb_students'] <= 7 or strategy['nb_students'] is NO_VALUE:
                self.flash(u'Auswertungen sind erst ab 7 Teilnehmer zulässig. Bitte erhöhen Sie die Anzahl der Teilnehmer auf mindestens 7')
                return FAILURE
            for student in clssession.generate_students(strategy['nb_students']):
                clssession.append(student)

        # update order
        for idx, criteria in enumerate(data.get('criterias', []), 1):
            query = criterias_table.update().where(
                criterias_table.c.courses_id == course.id
            ).where(
                criterias_table.c.criterias_id == criteria.id
            ).where(
                criterias_table.c.company_id == self.context.id
            ).values(order=idx)
            session.execute(query)

        self.flash(_(u'Course added with success.'))
        self.redirect(self.application_url())
        return SUCCESS


class CourseSession(Adapter):
    context(IClassSession)
    provides(ICourseSession)

    @apply
    def name():
        def fget(self):
            return self.context.course.name

        def fset(self, value):
            self.context.course.name = value
        return property(fget, fset)

    @apply
    def criterias():
        def fget(self):
            return self.context.course.criterias

        def fset(self, value):
            self.context.course.criterias = value
        return property(fget, fset)

    @apply
    def extra_questions():
        def fget(self):
            return self.context.course.extra_questions

        def fset(self, value):
            self.context.course.extra_questions = value
        return property(fget, fset)

    @apply
    def quizz_type():
        def fget(self):
            return self.context.course.quizz_type

        def fset(self, value):
            self.context.course.quizz_type = value
        return property(fget, fset)

    @apply
    def startdate():
        def fget(self):
            return self.context.startdate

        def fset(self, value):
            self.context.startdate = value
        return property(fget, fset)

    @apply
    def enddate():
        def fget(self):
            return self.context.enddate

        def fset(self, value):
            self.context.enddate = value
        return property(fget, fset)

    @apply
    def about():
        def fget(self):
            return self.context.about

        def fset(self, value):
            self.context.about = value
        return property(fget, fset)


@menuentry(IDocumentActions, order=10)
class EditCourse(Form):
    context(IClassSession)
    name('edit_course')
    require('manage.company')
    title(_(u'Edit the course'))
    title = label = "Befragung bearbeiten"
    description = u"Hier können Sie die Befragung bearbeiten"

    ignoreContent = False
    ignoreRequest = False

    dataManager = makeAdaptiveDataManager(ICourseSession)

    @property
    def fields(self):
        now = datetime.date.today()
        fields = Fields()
        if self.getContentData().content.context.enddate > now:
            fields += Fields(ICourseSession).select('enddate')
        if self.getContentData().content.startdate > now:
            fields += Fields(ICourseSession).select(
                'startdate', 'criterias', 'extra_questions')
            fields['extra_questions'].mode = "SpecialInput"
        fields += Fields(ICourseSession).select('about')
        return fields

    def update(self):
        wysiwyg.need()
        startendpicker.need()
        Form.update(self)

    @property
    def action_url(self):
        return self.request.path

    @action(u'Aktualisieren')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u"An error occured"))
            return FAILURE

        if 'extra_questions' in data:
            if data['extra_questions']:
                extra = data['extra_questions']
                if not extra:
                    data['extra_questions'] = None
            else:
                data['extra_questions'] = None

        apply_data_event(self.fields, self.getContentData(), data)
        self.flash(_(u"Der Inhalt wurde aktualisiert."))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.application_url())
        return SUCCESS


@menuentry(IDocumentActions, order=10)
class EditCourseBase(Form):
    context(Course)
    name('edit')
    require('manage.company')
    title(_(u'Edit the course'))

    ignoreContent = False
    ignoreRequest = False
    fields = Fields(ICourse).select('name', 'startdate')

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Update'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u"An error occured"))
            return FAILURE
        if 'extra_questions' not in data:
            data['extra_questions'] = None

        apply_data_event(self.fields, self.getContentData(), data)
        self.flash(_(u"Content updated"))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.url(self.context))
        return SUCCESS


@menuentry(IDocumentActions, order=20)
class DeleteCourse(DeleteForm):
    context(Course)
    name('delete')
    require('manage.company')
    title(_(u'Delete'))

    label = u"Befragung löschen"

    @property
    def description(self):
        return u"Wollen sie die Befragung %s wirklich löschen" % self.context.name

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')

        record = HistoryEntry(
            action=u"Delete",
            type=u"Course",
            description=u"Delete Course %s" % self.context.id)

        session.add(record)
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.application_url())
        return SUCCESS


@menuentry(IContextualActionsMenu, order=10)
class PopulateCourse(Form):
    context(IClassSession)
    name('populate')
    require('zope.Public')
    title(_(u'Add accesses'))
    order(3)

    fields = Fields(IPopulateCourse)

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Populate'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return
        for student in self.context.generate_students(data['nb_students']):
            self.context.append(student)
        self.flash(_(u'Added ${nb} accesses with success.',
                     mapping=dict(nb=data['nb_students'])))
        return self.redirect(self.url(self.context))


@menuentry(IDocumentActions, order=20)
class DeleteSession(DeleteForm):
    context(IClassSession)
    name('delete')
    require('manage.company')
    title(_(u'Delete'))

    label = u"Befragung löschen"

    @property
    def description(self):
        return u"Wollen sie die Befragung %s wirklich löschen" % self.context.title

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')

        record = HistoryEntry(
            action=u"Delete",
            type=u"Session",
            description=u"Delete Session %s" % self.context.id)

        session.add(record)
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.application_url())
        return SUCCESS


class SaveQuizz(Action):

    def available(self, form):
        from datetime import date
        today = date.today()
        return (today >= form.context.session.startdate and
                today <= form.context.session.enddate)

    def __call__(self, form):
        from collections import OrderedDict
        data, errors = form.extractData()
        if errors:
            form.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('school')

        fields = form.fields
        should_answers = {}
        extra_answers = OrderedDict()

        keys = data.keys()
        for key in keys:
            if key.startswith('criteria_'):
                cid = key.split('_', 1)[1]
                value = data.pop(key)
                field = fields.get(key)
                criteria_answer = CriteriaAnswer(
                    criteria_id=cid,
                    student_id=form.context.access,
                    session_id=form.context.session_id,
                    answer=value,
                    )
                session.add(criteria_answer)
            elif key.startswith('extra_'):
                value = data.pop(key)
                field = fields.get(key)
                extra_answers[field.description] = value
            elif key.startswith('should_'):
                value = data.pop(key)
                field = fields.get(key)
                should_answers[field.description] = value

        # We can't serialize sets
        # This could be done in a specific serializer
        # For now we do it in python.
        for key, value in extra_answers.items():
            if isinstance(value, set):
                extra_answers[key] = list(value)

        for key, value in should_answers.items():
            if isinstance(value, set):
                extra_answers[key] = list(value)
        data['extra_questions'] = json.dumps(extra_answers)
        if should_answers:
            data['should'] = json.dumps(should_answers)

        form.context.complete_quizz()
        quizz = form.quizz(**data)
        quizz.student_id = form.context.access
        quizz.company_id = form.context.company_id
        quizz.course_id = form.context.course_id
        quizz.session_id = form.context.session_id

        session.add(form.context)
        session.add(quizz)
        #form.flash(_(u'Thank you for answering the quizz'))
        form.redirect(form.request.url + '/finishquizz')
        return SUCCESS


class IAnonymousLogin(Interface):

    login = TextLine(
        title=_(u"Login Befragung"),
        description=u"Bitte geben Sie Ihr Kennwort ein um zur Befragung Ihres Unternehmens zu gelangen.",
        required=True,
        )

    
from nva.psyquizz.interfaces import QuizzAlreadyCompleted
class AnonymousLogin(Action):

    def available(self, form):
        return True

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.flash(_(u'An error occurred.'))
            return FAILURE
        student = form.context.get(data['login'])
        if student is not None:
            form.redirect('%s/%s' % (form.application_url(), data['login']))
            return SUCCESS
        else:
            form.flash(_(u'Falsches Kennwort'))
            return FAILURE


class AnonymousAccess(Form):
    context(QuizzBoard)
    layer(IAnonymousRequest)
    name('index')
    require('zope.Public')
    title(_(u'Login'))

    dataValidators = []
    fields = Fields(IAnonymousLogin)
    actions = Actions(AnonymousLogin(_(u'anmelden')))


class IQuizzFields(Interface):
    pass


class AnswerQuizz(Form):
    context(IQuizz)
    layer(IAnonymousRequest)
    name('index')
    require('zope.Public')
    title(_(u'Answer the quizz'))
    dataValidators = []
    template = get_template('wizard2.pt', __file__)

    fmode = 'radio'
    actions = Actions(SaveQuizz(_(u'Answer')))

    def update(self):
        course = self.context.course
        self.quizz = getUtility(IQuizz, name=course.quizz_type)
        self.titles = self.quizz.__schema__.queryTaggedValue('titles') or {}
        startdate = course.sessions[self.context.session_id].startdate
        if datetime.date.today() < startdate:
            self.flash(u'Die Befragung beginnt erst am %s deshalb werden Ihre Ergebnisse nicht gespeichert' % startdate.strftime('%d.%m.%Y'))
        Form.update(self)

    @property
    def action_url(self):
        return '%s/%s' % (self.request.script_name, self.context.access)

    @property
    def fields(self):
        fields = Fields(
            *self.quizz.base_fields(self.context.course))
        criteria_fields = Fields(
            *self.quizz.criteria_fields(self.context.course))
        extra_fields = Fields(
            *self.quizz.extra_fields(self.context.course))
        additional_extra_fields = Fields(
            *self.quizz.additional_extra_fields(self.context.course)
        )
        self.nbcriterias = len(criteria_fields)
        fields = criteria_fields + fields + additional_extra_fields + extra_fields

        for field in fields:
            if isinstance(field, ChoiceField):
                field.mode = self.fmode

        return fields


class CompanyAnswerQuizz(Action):

    def available(self, form):
        return True

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('school')

        # HERE WE CREATE THE STUDENT.
        from datetime import date
        from collections import OrderedDict
        uuid = Student.generate_access()
        student = Student(
            anonymous=True,
            access=uuid,
            completion_date=date.today(),
            company_id=form.context.course.company_id,
            session_id=form.context.id,
            course=form.context.course,
            course_id=form.context.course.id,
            quizz_type=form.context.course.quizz_type)

        fields = form.fields
        extra_answers = OrderedDict()
        keys = data.keys()
        for key in keys:
            if key.startswith('criteria_'):
                cid = key.split('_', 1)[1]
                value = data.pop(key)
                field = fields.get(key)
                criteria_answer = CriteriaAnswer(
                    criteria_id=cid,
                    student_id=student.access,
                    session_id=student.session_id,
                    answer=value,
                    )
                session.add(criteria_answer)
            elif key.startswith('extra_'):
                value = data.pop(key)
                field = fields.get(key)
                if isinstance(value, set):
                    value = list(value)
                extra_answers[field.description] = value

        data['extra_questions'] = json.dumps(extra_answers)

        student.complete_quizz()
        quizz = form.quizz(**data)
        quizz.student_id = student.access
        quizz.company_id = student.company_id
        quizz.course_id = student.course_id
        quizz.session_id = student.session_id

        session.add(student)
        session.add(quizz)
        form.flash(_(u'Eingabe wurde gespeichert.'))
        form.redirect(form.request.url)
        return SUCCESS
