# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import os.path
import json
import uvclight
import xlsxwriter
import cStringIO
import itertools
import shutil
from backports import tempfile

from collections import OrderedDict, namedtuple
from cromlech.browser import IView
from grokcore.component import name, provider
from nva.psyquizz import hs
from nva.psyquizz.models import IQuizz, IClassSession, ICourse
from nva.psyquizz.models.quizz.quizz2 import Quizz2
from nva.psyquizz.models.quizz.quizz1 import Quizz1
from uvclight.auth import require
from zope.component import getUtility, getMultiAdapter
from zope.interface import Interface
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.location import LocationProxy

from ..interfaces import ICompanyRequest
from ..stats import compute, groups_scaling
from zope.schema import Choice
from dolmen.forms.base import FAILURE, SUCCESS
from nva.psyquizz.i18n import MessageFactory as _


CHUNK = 4096


Result = namedtuple(
    'Result',
    ('answer', 'id', 'result', 'result_title'))


Average = namedtuple(
    'Average',
    ('title', 'average'))


def average_computation(data):
    for k, v in data.items():
        yield Average(k, float(sum([x.result for x in v]))/len(v))


def sort_data(order, data):

    def sorter(id):
        for k, v in order.items():
            if id in v:
                return k

    ordered = OrderedDict()
    for id, values in data.items():
        title = sorter(id)
        current = ordered.setdefault(title, [])
        current += values

    return ordered


class Scale(object):

    percentage = 0
    number = 0

    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


class Statistics(object):

    averages = OrderedDict((
        (u'Vielseitiges Arbeiten', ('1', '2', '3')),
        (u'Ganzheitliches Arbeiten', ('4', '5')),
        (u'Passende inhaltliche Arbeitsanforderungen', ('6', '7')),
        (u'Passende mengenmäßige Arbeit', ('8', '9')),
        (u'Passende Arbeitsabläufe', ('10', '11')),
        (u'Passende Arbeitsumgebung', ('12', '13')),
        (u'Handlungsspielraum', ('14', '15', '16')),
        (u'Soziale Rückendeckung', ('17', '18', '19')),
        (u'Zusammenarbeit', ('20', '21', '22')),
        (u'Information und Mitsprache', ('23', '24')),
        (u'Entwicklungsmöglichkeiten', ('25', '26')),
        ))


def get_filters(request):

    def extract_criteria(str):
        cid, name = str.split(':', 1)
        return str, int(cid), name

    filters = {}
    Criteria = namedtuple('Criteria', ('id', 'name'))
    criterias = request.form.get('criterias', None)
    if criterias is not None:
        if not isinstance(criterias, (set, list, tuple)):
            criterias = [criterias]
        filters['criterias'] = {
            uid: Criteria(cid, name) for uid, cid, name in
            map(extract_criteria, criterias)}
    return filters


class CourseStatistics(object):

    def __init__(self, quizz, course, request):
        self.quizz = quizz
        self.averages = quizz.__schema__.getTaggedValue('averages')
        self.course = course
        self.request = request
        session_ids = [x.id for x in self.course.sessions]

    def update(self, filters):
        self.filters = filters
        self.statistics = compute(
            self.quizz, self.averages, self.filters)
        self.users_statistics = groups_scaling(
            self.statistics['users.grouped'])
        self.xAxis = [
        x.encode('iso-8859-1') for x in self.users_statistics.keys() if x]
        good = dict(name="viel / zutreffend", data=[], color="#62B645")
        mid = dict(name="mittelmäßig", data=[], color="#FFCC00")
        bad = dict(name="wenig / nicht zutreffend", data=[], color="#D8262B")
        for x in self.users_statistics.values():
            good['data'].append(x[0].percentage)
            mid['data'].append(x[1].percentage)
            bad['data'].append(x[2].percentage)
        self.series = json.dumps([good, mid, bad])
        self.rd1 = [x.average for x in self.statistics['global.averages']]
        self.rd = [float("%.2f" % x.average) for x in self.statistics['global.averages']]

        criterias = []
        for crits in self.statistics['criterias'].values():
            for crit in crits:
                criterias.append([crit.name, crit.amount])
        self.json_criterias = json.dumps(criterias)


class SessionStatistics(CourseStatistics):

    def __init__(self, quizz, session, request):
        self.quizz = quizz
        self.course = session.course
        self.session = session
        self.averages = quizz.__schema__.getTaggedValue('averages')
        self.request = request

    def update(self, filters):
        filters['session'] = self.session.id
        return CourseStatistics.update(self, filters)
        

DOKU_TEXT = u"""Falls Sie die Kennwörter nicht mit Hilfe des Serienbriefes verteilen möchten können
Sie diese Excel Liste für eine alternative Form der Verteilung nutzen, z.B. Serien E-
Mail (Funktion ist nicht Bestandteil des Online Tools) nutzen.
Unter „Kennwörter“ finden Sie eine Übersicht der für den Zugang zur Befragung
benötigten Kennwörter. Unter „Links & Kennwörter“ sind Link und individuelles
Kennwort zusammengeführt, so dass sich nach Klick auf den Link direkt der
Fragebogen öffnen lässt."""

class DownloadTokens(uvclight.View):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        app_url = self.application_url()
        _all = itertools.chain(
            self.context.uncomplete, self.context.complete)
        self.tokens = ['%s/quizz/%s' % (app_url, a.access) for a in _all]

    def generateXLSX(self, folder, filename="ouput.xlsx"):
        filepath = os.path.join(folder, filename)
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet(u'Dokumentation')
        worksheet.insert_textbox(0, 0, DOKU_TEXT, {'width': 450, 'height': 700, 'font': {'size': 13}})
        worksheet = workbook.add_worksheet(u'Kennwörter')
        for i, x in enumerate(self.tokens):
            worksheet.write(i, 0, x.split('/')[-1:][0])
        worksheet = workbook.add_worksheet(u'Links & Kennwörter')
        for i, x in enumerate(self.tokens):
            worksheet.write(i, 0, x)
        
        workbook.close()
        return filepath

    def render(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = self.generateXLSX(temp_dir)
            output = cStringIO.StringIO()
            with open(filepath, 'rb') as fd:
                shutil.copyfileobj(fd, output)
            output.seek(0)
        return output

    def make_response(self, result):
        response = self.responseFactory()
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = (
            u'attachment; filename="Kennwortliste.xlsx"')

        def filebody(r):
            data = r.read(CHUNK)
            while data:
                yield data
                data = r.read(CHUNK)

        response.app_iter = filebody(result)
        return response

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak
from tempfile import TemporaryFile
from dolmen.forms.base.actions import Action, Actions
from zope.interface import Interface
from zope.schema import Text
from cromlech.browser.interfaces import IResponse
from cromlech.browser.exceptions import HTTPRedirect
from cromlech.browser.utils import redirect_exception_response


class GenerateLetter(Action):

    def generate(self, tokens, text, form):
        style = getSampleStyleSheet()
        nm = style['Normal']
        nm.leading = 14
        story = []
        print text
        for i, x in enumerate(tokens):
            #story.append(Paragraph('Serienbrief', style['Heading1']))
            story.append(Paragraph(text.replace('<br>','<br/>').replace('</p>', '</p><br/>'), nm))
            story.append(Paragraph('Die Internetadresse lautet: <b> %s/quizz</b> <br/> Ihr Kennwort lautet: <b> %s</b> ' % (form.application_url(), x), nm))
            story.append(PageBreak())
        tf = TemporaryFile()
        pdf = SimpleDocTemplate(tf, pagesize=A4)
        pdf.build(story)
        tf.seek(0)
        return tf

    def tokens(self, form):
        _all = itertools.chain(
            form.context.complete, form.context.uncomplete)
        return ['%s' % (a.access) for a in _all]
    
    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.flash(u"Es ist ein Fehler aufgetreten")
            return FAILURE

        tokens = self.tokens(form)
        data = self.generate(tokens, data['text'] + '<br />', form)
        response = form.responseFactory(app_iter=data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; \
                filename="serienbrief.pdf"'
        return response


DEFAULT = u"""
<p><b>Liebe Kolleginnen und Kollegen, </b></p>
<p>wie bereits angekündigt, erhalten Sie heute Ihre Einladung zur Teilnahme an unserer Befragung „Gemeinsam zu gesunden Arbeitsbedingungen“.</p>
<p>Ziel der Befragung ist es, Ihre Arbeitsbedingungen zu beurteilen und ggf. entsprechende Verbesserungsmaßnahmen einleiten zu können. Bitte beantworten Sie alle Fragen off
<p> Keine Mitarbeiterin und kein Mitarbeiter unserer Firma wird Einblick in die originalen Datensätze erhalten, eine Rückverfolgung wird nicht möglich sein.</p>
<p>Die Aussagekraft der Ergebnisse hängt von einer möglichst hohen Beteiligung ab. Geben Sie Ihrer Meinung Gewicht!</p>
<p>Die Befragung läuft vom %s - %s . Während dieses Zeitraums haben Sie die Möglichkeit, über folgende Internetadresse an unserer Befragung teilzunehmen:
<br/>

<p>Über diesen Link gelangen Sie direkt auf den Fragebogen unseres Unternehmens. Das Ausfüllen wird etwa 5 Minuten in Anspruch nehmen. </p>
<p>Nehmen Sie sich diese Zeit, Ihre Meinung zu äußern, wir freuen uns auf Ihre Rückmeldung und bedanken uns bei Ihnen für Ihre Mitarbeit!</p>
<p>Sollten Sie Fragen oder Anmerkungen haben, wenden Sie sich bitte an:</p> <p><span> A n s p r e c h p a r t n e r   &nbsp;    und   &nbsp;     K o n t a k t d a t e n </span></p>
"""

from nva.psyquizz.models.interfaces import v_about

class ILetter(Interface):
    text = Text(title=u" ", required=True, constraint=v_about)
    


DESC = u"""Nutzen Sie die folgende (anpassbaren) Vorlage, um Ihre Beschäftigten über die Befragung zu informieren.
Über die Funktion „Serienbrief erstellen“, wird eine PDF Datei mit Anschreiben für jeden
Beschäftigten - inkl. Link zur Befragung und einem individuellen Kennwort - erzeugt. Drucken
Sie die Anschreiben aus und verteilen Sie diese an die Beschäftigten.
"""


from nva.psyquizz import  wysiwyg 


class DownloadLetter(uvclight.Form):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)
    label = u"Serienbrief"
    description = DESC

    fields = uvclight.Fields(ILetter)
    actions = Actions(GenerateLetter('Serienbrief erstellen'))
    ignoreContent = False

    def update(self):
        from dolmen.forms.base.datamanagers import DictDataManager
        DE = DEFAULT % (
            self.context.startdate.strftime('%d.%m.%Y'),
            self.context.enddate.strftime('%d.%m.%Y'),
            )
        defaults = dict(text=DE)
        self.setContentData(
            DictDataManager(defaults))

    def updateForm(self):
        wysiwyg.need()
        action, result = self.updateActions()
        if IResponse.providedBy(result):
            return result
        self.updateWidgets()

    def __call__(self, *args, **kwargs):
        try:
            self.update(*args, **kwargs)
            response = self.updateForm()
            if response is not None:
                return response
            result = self.render(*args, **kwargs)
            return self.make_response(result, *args, **kwargs)
        except HTTPRedirect, exc:
            return redirect_exception_response(self.responseFactory, exc)


class XSLX(object):

    def generateXLSX(self, folder, filename="Ergebnischart.xlsx"):
        filepath = os.path.join(folder, filename)
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet('Dokumentation')

        worksheet.write(0,0, 'Datenbasis')

        amounts = dict(json.loads(self.json_criterias))
        ii = 1
        for k,v in self.filters.get('criterias', {}).items():
            worksheet.write(ii, 0,  "%s %s" % (v.name, amounts.get(v.name)))
            ii += 1


        worksheet = workbook.add_worksheet('Mittelwerte')
        nformat = workbook.add_format()
        nformat.set_num_format('0.00')

        # Add a format for the header cells.
        header_format = workbook.add_format({
            'border': 1,
            'bg_color': '#C6EFCE',
            'bold': True,
            'text_wrap': True,
            'valign': 'vcenter',
            'indent': 1,
            'locked': 1,
        })

        question_format = workbook.add_format({
            'border': 0,
            'color': '#000000',
            'bold': True,
            'text_wrap': False,
            'valign': 'vcenter',
            'indent': 0,
            'locked': 1,
        })
        
        for i, x in enumerate(self.statistics['global.averages']):
            worksheet.write(i, 0, x.title)
            worksheet.write(i, 1, x.average, nformat)

        chart1 = workbook.add_chart({'type': 'radar'})
        chart1.add_series({
            'name':       'Mittelwerte',
            'categories': '=Mittelwerte!$A$1:$A$11',
            'values':     '=Mittelwerte!$B$1:$B$11',
            'min': 1,
            })

        chart1.set_title({'name': 'Durchschnitt'})
        chart1.set_x_axis({'name': 'Test number', "min": 1})
        chart1.set_y_axis({'name': 'Sample length (mm)', "min": 1})
        chart1.set_style(11)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('A13', chart1, {'x_offset': 25, 'y_offset': 10})

        worksheet = workbook.add_worksheet('Verteilung')

        data = json.loads(self.series)
        for y, x in enumerate(data):
            name = x['name']
            r = 1 
            worksheet.write(0, y, name)
            for i, z in enumerate(x['data']):
                worksheet.write((r+1+i), y, z)

        for idx, titel in enumerate(self.xAxis):
            worksheet.write((idx + 2), 3, unicode(titel, 'latin1'))

        #worksheet = workbook.add_worksheet('Verteilung')

        chart3 = workbook.add_chart(
            {'type': 'bar', 'subtype': 'percent_stacked'})

        chart3.set_title({'name': 'Verteilung'})

        # Configure the first series.
        chart3.add_series({
            'name':       '=Verteilung!$A$1',
            'categories': '=Verteilung!$D$3:$D$13',
            'values':     '=Verteilung!$A$3:$A$13',
            'fill':   {'color': data[2]['color']},
        })

        chart3.add_series({
            'name':       '=Verteilung!$B$1',
            'categories': '=Verteilung!$D$3:$D$13',
            'values':     '=Verteilung!$B$3:$B$13',
            'fill':   {'color': data[1]['color']},
        })

        chart3.add_series({
            'name':       '=Verteilung!$C$1',
            'categories': '=Verteilung!$D$3:$D$13',
            'values':     '=Verteilung!$C$3:$C$13',
            'fill':   {'color': data[0]['color']},
        })

        chart3.set_y_axis({'reverse': True})
        worksheet.insert_chart("A20", chart3, {'x_offset': 15, 'y_offset': 10})

        worksheet = workbook.add_worksheet('Mittelwerte pro Frage')
        offset = 1 
        
        if 'criterias' in self.filters:
            for cname, cvalues in self.statistics['criterias'].items():
                for v in cvalues:
                    offset += 1
                    worksheet.write("A%i" % offset, cname)
                    worksheet.write("B%i" % offset, v.name)
                    worksheet.write("C%i" % offset, v.amount)
        else:
            offset += 1
            worksheet.write("A%i" % offset , "ALL CRITERIAS")

        offset += 2
        worksheet.write("A%i" % offset, "Frage")
        worksheet.write("B%i" % offset, "Mittelwert")
        
        labels = {k.title: k.description for id, k in
                  getFieldsInOrder(self.quizz.__schema__)}
        for avg in self.statistics['per_question_averages']:
            offset += 1
            assert avg.title in labels
            worksheet.write("A%i" % offset, labels[avg.title])
            worksheet.write("B%i" % offset, avg.average, nformat)

        #worksheet = workbook.add_worksheet('RAW')
        #worksheet.set_column('A:A', 25)
        #worksheet.set_column('B:END', 30)
        
        #worksheet.write(0, 0, "Questions", header_format)
        
        #for i in range(1, self.statistics['total'] + 1, 1):
        #    worksheet.write(0, i, "Student %s" % i, header_format)
        
        #for question, answers in self.statistics['raw'].items():
        #    line = int(question)
        #    worksheet.write(line, 0, "Question %s" % question, question_format)
        #    for idx, answer in enumerate(answers, 1):
        #        worksheet.write(line, idx, answer.result_title)
 
        workbook.close()
        return filepath

    def render(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = self.generateXLSX(temp_dir)
            output = cStringIO.StringIO()
            with open(filepath, 'rb') as fd:
                shutil.copyfileobj(fd, output)

            output.seek(0)
        return output


class CourseXSLX(CourseStatistics, XSLX):
    name('xslx')
    

class SessionXSLX(SessionStatistics, XSLX):
    name('xslx')


class Quizz2Charts(uvclight.Page):
    require('manage.company')
    name('charts')
    uvclight.context(Quizz2)

    template = uvclight.get_template('cr.pt', __file__)
    general_stats = None

    def jsonify(self, da):
        return json.dumps(da)

    def update(self, stats, general_stats=None):
        hs.need()
        self.stats = stats
        self.general_stats = general_stats


class Quizz1Charts(uvclight.Page):
    require('manage.company')
    name('charts')
    uvclight.context(Quizz1)

    template = uvclight.get_template('cr1.pt', __file__)

    def jsonify(self, da):
        return json.dumps(da)

    def update(self, stats, general_stats=None):
        hs.need()
        self.stats = stats
        self.general_stats = general_stats

        good = dict(name="Eher Ja", data=[], color="#62B645")
        bad = dict(name="Eher Nein", data=[], color="#D8262B")

        xAxis = []
        percents = {}

        self.descriptions = json.dumps(self.context.__schema__.getTaggedValue('descriptions'))
        self.xAxis_labels = {k.title: k.description for id, k in getFieldsInOrder(self.context.__schema__)}

        for key, answers in self.stats.statistics['raw'].items():
            xAxis.append(key)
            yesses = 0
            noes = 0
            total = 0
            for answer in answers:
                total += 1
                if answer.result is True:
                    yesses += 1
                else:
                    noes +=1 

            good['data'].append(float(yesses)/total * 100)
            bad['data'].append(float(noes)/total * 100)

        self.xAxis = json.dumps(xAxis)
        self.series = json.dumps([good, bad])


class SR(uvclight.Page):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        quizz = getUtility(IQuizz, self.context.course.quizz_type)
        filters = get_filters(self.request)
        stats = SessionStatistics(quizz, self.context, self.request)
        stats.update(filters)

        if 'criterias' in filters:
            general_stats = SessionStatistics(quizz, self.context, self.request)
            general_stats.update({})
        else:
            general_stats = None

        quizz_obj = LocationProxy(quizz(), container=self.context, name='')
        self.charts = getMultiAdapter(
            (quizz_obj, self.request), IView, name="charts")
        self.charts.update(stats, general_stats)

    def render(self):
        return self.charts.render()


class CR(uvclight.Page):
    require('manage.company')
    uvclight.context(ICourse)
    uvclight.layer(ICompanyRequest)

    template = uvclight.get_template('cr.pt', __file__)
    general_stats = None

    def jsonify(self, da):
        return json.dumps(da)

    def update(self):
        hs.need()
        quizz = getUtility(IQuizz, self.context.quizz_type)
        filters = get_filters(self.request)
        stats = CourseStatistics(quizz, self.context)
        stats.update(filters)

        if 'criterias' in filters:
            general_stats = CourseStatistics(quizz, self.context, self.request)
            general_stats.update({})
        else:
            general_stats = None

        self.charts = getMultiAdapter(
            (quizz, self.request), IView, name="charts")
        self.charts.update(stats, general_stats)

    def render(self):
        return self.charts.render()


class Export(uvclight.View):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        action = self.request.form.get('action', None)
        assert action is not None
        if action == 'PDF':
            self.view = getMultiAdapter(
                (self.context, self.request), name="pdf")
            self.view.update()
        elif action == 'Excel':
            self.view = getMultiAdapter(
                (self.context, self.request), name="excel")
            self.view.update()
        else:
            raise NotImplementedError('Action unknown')

    def render(self):
        return self.view.render()

    def make_response(self, result):
        return self.view.make_response(result)


class Excel(uvclight.Page):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = SessionXSLX(quizz, self.context, self.request)
        filters = get_filters(self.request)
        self.stats.update(filters)

    def render(self):
        return self.stats.render()

    def make_response(self, result):
        response = self.responseFactory()
        response.headers['Content-Type'] = (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response.headers['Content-Disposition'] = (
            u'attachment; filename="Resultate_Befragung.xlsx"')

        def filebody(r):
            data = r.read(CHUNK)
            while data:
                yield data
                data = r.read(CHUNK)

        response.app_iter = filebody(result)
        return response


@provider(IContextSourceBinder)
def courses(context):
    return SimpleVocabulary([
        SimpleTerm(value=c, token=c.id, title=c.name)
        for c in context.company.courses if c.id != context.id])


class ICourseDiff(Interface):

    course = Choice(
        title=u"Course to diff with",
        required=True,
        source=courses)


class CDiff(uvclight.Form):
    require('manage.company')
    uvclight.context(ICourse)
    uvclight.layer(ICompanyRequest)

    fields = uvclight.Fields(ICourseDiff)
    template = uvclight.get_template('cdiff.cpt', __file__)

    current = None
    diff = None

    @property
    def action_url(self):
        return self.request.path

    @uvclight.action(u'Difference')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u'An error occurred.'))
            return FAILURE

        hs.need()
        quizz = getUtility(IQuizz, self.context.quizz_type)
        # This course
        self.current = CourseStatistics(quizz, self.context)
        self.current.update(self.request)

        # The diff course
        self.diff = CourseStatistics(quizz, data['course'])
        self.diff.update(self.request)
        return SUCCESS
