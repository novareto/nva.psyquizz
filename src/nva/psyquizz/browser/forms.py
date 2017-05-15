# -*- coding: utf-8 -*-

from uvc.protectionwidgets import Captcha
import os
import json
import uuid
import datetime
import html2text

from .. import wysiwyg, quizzjs, startendpicker
from ..apps.anonymous import QuizzBoard
from ..i18n import _
from ..interfaces import IAnonymousRequest, ICompanyRequest
from ..interfaces import QuizzAlreadyCompleted, QuizzClosed
from ..interfaces import IRegistrationRequest
from ..models import Account, Company, Course, ClassSession, Student
from ..models import ICourseSession, IAccount, ICompany, ICourse, IClassSession
from ..models import IQuizz, TrueOrFalse
from ..models import Criteria, CriteriaAnswer, ICriteria, ICriterias
from .emailer import SecureMailer, prepare, ENCODING

from cromlech.sqlalchemy import get_session
from dolmen.forms.base import SuccessMarker, makeAdaptiveDataManager
from dolmen.forms.base.actions import Action, Actions
from dolmen.forms.base.errors import Error
from dolmen.forms.base.utils import apply_data_event
from dolmen.forms.crud.actions import message
from dolmen.menu import menuentry, order
from grokcore.component import Adapter, provides, context
from nva.psyquizz import quizzjs
from siguvtheme.resources import all_dates, datepicker_de
from string import Template
from uvc.design.canvas import IContextualActionsMenu
from uvc.design.canvas import IDocumentActions
from uvclight import Form, EditForm, DeleteForm, Fields, SUCCESS, FAILURE
from uvclight import action, layer, name, title, get_template
from uvclight.auth import require
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import provider
from zope.schema import Int, Choice, Password, TextLine
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary


with open(os.path.join(os.path.dirname(__file__), 'mail.tpl'), 'r') as fd:
    data = unicode(fd.read(), 'utf-8')
    mail_template = Template(data.encode(ENCODING))


def send_activation_code(company_name, email, code, base_url):
    mailer = SecureMailer('smtprelay.bg10.bgfe.local')  # BBB
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
        print mail.as_string()
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
        SimpleTerm('fixed', 'fixed', u'Feste Anzahl pro Teilnehmer'),
        SimpleTerm('mixed', 'mixed', u'Feste und freie Anzahl von Teilnehmern'),
        SimpleTerm('free', 'free', u'Freie Anzahl von Teilnehmern'),
    ))


class IPopulateCourse(Interface):

    strategy = Choice(
        title=u"Strategie",
        description=u"Hier können Sie auswählen welche Stragie Sie für das Einrichen von Fragebögen gelten soll.",
        source=get_strategy,
    )

    nb_students = Int(
        title=_(u"Number of students"),
        required=True,
        )


@menuentry(IContextualActionsMenu, order=10)
class CreateCriterias(Form):
    context(ICriterias)
    name('add.criteria')
    title(_(u'Add a criteria'))
    require('zope.Public')

    fields = Fields(ICriteria).select('title', 'items')
    label = u"Auswertungsgruppen anlegen"
    description = u"""
   Bitte geben Sie zunächst einen Oberbegriff für Ihre Auswertungsgruppen an, wie z.B. „Abteilung“. Zu 
jedem Oberbegriff gehören mindestens zwei Auswertungsgruppen. Zum Oberbegriff „Abteilung“ 
könnten bspw. die Auswertungsgruppen „Personalabteilung“ und „Produktion“ gehören.  
<b>Beachten Sie bei der Wahl Ihrer Auswertungsgruppen - aus Datenschutzgründen werden Ihnen nur 
Ergebnisse von Auswertungsgruppen angezeigt, von denen mindestens sieben ausgefüllte 
„Fragebogen“ vorliegen.</b>
    """

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
        criteria = Criteria(**data)
        criteria.company_id = self.context.__parent__.id
        session.add(criteria)
        session.flush()
        session.refresh(criteria)
        self.flash(_(u'Criteria added with success.'))
        self.redirect(self.application_url())
        return SUCCESS


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

    fields = Fields(IClassSession).select('startdate', 'enddate', 'about')

    def update(self):
        #all_dates.need()
        #datepicker_de.need()
        startendpicker.need()
        wysiwyg.need()
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
        clssession = ClassSession(**data)
        clssession.course_id = self.context.id
        clssession.company_id = self.context.__parent__.id
        session.add(clssession)
        session.flush()
        session.refresh(clssession)
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

        existing = session.query(Account).get(data['email'])
        if existing is not None:
            self.flash(_(u'User with given email already exists.'))
            self.errors.append(
                Error(identifier='form.field.email',
                      title='Diese E-Mail Adresse existiert bereits im System.'))
            return FAILURE

        # pop the captcha and verif, it's not a needed data
        data.pop('verif')
        data.pop('captcha')

        account = Account(**data)
        code = account.activation = str(uuid.uuid1())
        session.add(account)
        session.flush()
        session.refresh(account)

        base_url = self.application_url().replace('/register', '')
        send_activation_code(data['name'], data['email'], code, base_url)
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

    dataValidators = []
    fields = Fields(ICompany).select(
        'name', 'mnr', 'exp_db', 'type', 'employees')
    fields['mnr'].htmlAttributes = {'maxlength': 8}

    def updateForm(self):
        super(CreateCompany, self).updateForm()
        self.fieldWidgets.get('form.field.exp_db').template = get_template(
            'checkbox.cpt', __file__)
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
class CreateCourse(Form):
    context(Company)
    name('add.course')
    require('manage.company')
    title(_(u'Add a course'))

    @property
    def fields(self):
        course_fields = Fields(ICourse).select(
            'name', 'criterias', 'quizz_type')
        course_fields['criterias'].mode = "INOUT"
        populate_fields = Fields(IPopulateCourse)
        populate_fields['strategy'].mode = "radio"
        session_fields = Fields(IClassSession).select(
            'startdate', 'enddate', 'about')
        return course_fields + populate_fields + session_fields

    def update(self):
        all_dates.need()
        datepicker_de.need()
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
        csdata = dict(
            startdate=data.pop('startdate'),
            enddate=data.pop('enddate'),
            about=data.pop('about'),
            strategy=data.pop('strategy')
        )
        strategy = dict(
           nb_students=data.pop('nb_students'),
           strategy=csdata.get('strategy')
        )
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
            for student in clssession.generate_students(strategy['nb_students']):
                clssession.append(student)
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
    def duration():
        def fget(self):
            return self.context.duration

        def fset(self, value):
            self.context.duration = value
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

    ignoreContent = False
    ignoreRequest = False

    dataManager = makeAdaptiveDataManager(ICourseSession)

    @property
    def fields(self):
        now = datetime.date.today()
        fields = Fields(ICourseSession).select('duration', 'about')
        if self.getContentData().content.startdate > now:
            fields += Fields(ICourseSession).select('startdate', 'criterias')
        return fields

    def update(self):
        all_dates.need()
        datepicker_de.need()
        wysiwyg.need()
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

    fields = Fields(ICourse).select(
        'name', 'startdate')

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Update'))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u"An error occured"))
            return FAILURE

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

    @property
    def action_url(self):
        return self.request.path

    @action(_(u'Delete'))
    def handle_save(self):
        session = get_session('school')
        session.delete(self.context)
        session.flush()
        self.flash(_(u'Deleted with success.'))
        self.redirect(self.application_url())
        return SUCCESS

    @action(_(u'Cancel'))
    def handle_cancel(self):
        self.redirect(self.url(self.application_url()))
        return SUCCESS


class SaveQuizz(Action):

    def available(self, form):
        from datetime import date
        today = date.today()
        return (today >= form.context.session.startdate and
                today <= form.context.session.enddate)

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.flash(_(u'An error occurred.'))
            return FAILURE

        session = get_session('school')

        fields = form.fields
        extra_answers = {}

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
                extra_answers[field.title] = value

        data['extra_questions'] = json.dumps(extra_answers)

        form.context.complete_quizz()
        quizz = form.quizz(**data)
        quizz.student_id = form.context.access
        quizz.company_id = form.context.company_id
        quizz.course_id = form.context.course_id
        quizz.session_id = form.context.session_id

        session.add(form.context)
        session.add(quizz)
        form.flash(_(u'Thank you for answering the quizz'))
        form.redirect(form.request.url)
        return SUCCESS


class IAnonymousLogin(Interface):

    login = TextLine(
        title=_(u"Login"),
        required=True,
        )

    
class AnonymousLogin(Action):

    def available(self, form):
        return True

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.flash(_(u'An error occurred.'))
            return FAILURE

        try:
            student = form.context.create_student(data['login'])
        except QuizzClosed:
            form.flash(_(u'This session is no longer available'))
            return FAILURE
        except AssertionError:
            form.flash(_(u'Invalid token'))
            return FAILURE
        except Exception as ex:
            form.flash(_(u'Invalid token'))
            return FAILURE
        
        form.redirect('%s/%s' % (form.request.url, student.access))
        return SUCCESS


class AnonymousAccess(Form):
    context(QuizzBoard)
    layer(IAnonymousRequest)
    name('index')
    require('zope.Public')
    title(_(u'Login'))

    dataValidators = []
    fields = Fields(IAnonymousLogin)
    actions = Actions(AnonymousLogin(_(u'Login')))


    
class AnswerQuizz(Form):
    context(Student)
    layer(IAnonymousRequest)
    name('index')
    require('zope.Public')
    title(_(u'Answer the quizz'))
    dataValidators = []
    template = get_template('wizard2.pt', __file__)

    actions = Actions(SaveQuizz(_(u'Answer')))

    def update(self):
        course = self.context.course
        self.quizz = getUtility(IQuizz, name=course.quizz_type)
        startdate = course.sessions[self.context.session_id].startdate
        if datetime.date.today() < startdate:
            self.flash(u'Die Befragung beginnt erst am %s deshalb werden Ihre Ergebnisse nicht gespeichert' % startdate.strftime('%d.%m.%Y'))
        Form.update(self)

    @property
    def action_url(self):
        return '%s/%s' % (self.request.script_name, self.context.access)

    @property
    def fields(self):
        fields = Fields(self.quizz.__schema__)
        fields.sort(key=lambda c: c.interface[c.identifier].order)

        criteria_fields = []
        for criteria in self.context.course.criterias:
            values = SimpleVocabulary([
                    SimpleTerm(value=c.strip(), token=idx, title=c.strip())
                    for idx, c in enumerate(criteria.items.split('\n'), 1)
                    if c.strip()])

            criteria_field = Choice(
                __name__='criteria_%s' % criteria.id,
                title=criteria.title,
                description=u"Wählen Sie das Zutreffende aus.",
                vocabulary=values,
                required=True,
            )
            criteria_fields.append(criteria_field)
        self.nbcriterias = len(criteria_fields)
        fields = Fields(*criteria_fields) + fields

        questions_text = self.context.course.extra_questions
        questions_fields = []
        if questions_text:
            questions = questions_text.strip().split('\n')
            for idx, question in enumerate(questions, 1):
                question = question.decode('utf-8').strip()
                extra_field = Choice(
                    __name__='extra_question%s' % idx,
                    title=question,
                    vocabulary=TrueOrFalse,
                    required=True,
                    )
                questions_fields.append(extra_field)
        fields += Fields(*questions_fields)

        for field in fields:
            field.mode = 'radio'

        return fields
