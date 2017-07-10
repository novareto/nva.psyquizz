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

    def __init__(self, quizz, course):
        self.quizz = quizz
        self.averages = quizz.__schema__.getTaggedValue('averages')
        self.course = course
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

    def __init__(self, quizz, session):
        self.quizz = quizz
        self.course = session.course
        self.session = session
        self.averages = quizz.__schema__.getTaggedValue('averages')

    def update(self, filters):
        filters['session'] = self.session.id
        return CourseStatistics.update(self, filters)
        

class DownloadTokens(uvclight.View):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        app_url = self.application_url()
        _all = itertools.chain(
            self.context.uncomplete, self.context.uncomplete)
        self.tokens = ['%s/quizz/%s' % (app_url, a.access) for a in _all]

    def generateXLSX(self, folder, filename="ouput.xlsx"):
        filepath = os.path.join(folder, filename)
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet(u'Kennwörter')
        for i, x in enumerate(self.tokens):
            worksheet.write(i, 0, x.split('/')[-1:][0])
        worksheet = workbook.add_worksheet(u'Links')
        for i, x in enumerate(self.tokens):
            worksheet.write(i, 0, x)
        worksheet = workbook.add_worksheet(u'Dokumentation')
        text = 'DOKUMENTATION TBD'
        worksheet.insert_textbox(1, 1, text)
        
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
            u'attachment; filename="tokens.xlsx"')

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

class DownloadLetter(uvclight.View):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        app_url = self.application_url()
        _all = itertools.chain(
            self.context.uncomplete, self.context.uncomplete)
        self.tokens = ['%s' % (a.access) for a in _all]

    def make_response(self, result):
        response = self.responseFactory(app_iter=result)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; \
                filename="kfza.pdf"'
        return response

    def render(self):
        style = getSampleStyleSheet()
        story = []
        for i, x in enumerate(self.tokens):
            story.append(Paragraph('Serienbrief', style['Heading1']))
            import pdb; pdb.set_trace() 
            story.append(Paragraph(x, style['Normal']))
            story.append(PageBreak())
        tf = TemporaryFile()
        pdf = SimpleDocTemplate(tf, pagesize=A4)
        pdf.build(story)
        tf.seek(0)
        return tf



class XSLX(object):

    def generateXLSX(self, folder, filename="ouput.xlsx"):
        filepath = os.path.join(folder, filename)
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet()

        for i, x in enumerate(self.statistics['global.averages']):
            worksheet.write(i, 0, x.title)
            worksheet.write(i, 1, x.average)

        chart1 = workbook.add_chart({'type': 'radar'})
        chart1.add_series({
            'name':       'Durchscnitt',
            'categories': '=Sheet1!$A$1:$A$11',
            'values':     '=Sheet1!$B$1:$B$11',
            })

        chart1.set_title({'name': 'Results of sample analysis'})
        chart1.set_x_axis({'name': 'Test number'})
        chart1.set_y_axis({'name': 'Sample length (mm)'})
        chart1.set_style(11)

        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart('A13', chart1, {'x_offset': 25, 'y_offset': 10})

        data = json.loads(self.series)
        for y, x in enumerate(data):
            name = x['name']
            r = 27
            worksheet.write(27, y, name)
            for i, z in enumerate(x['data']):
                worksheet.write((r+1+i), y, z)

        chart3 = workbook.add_chart(
            {'type': 'bar', 'subtype': 'percent_stacked'})

        # Configure the first series.
        chart3.add_series({
            'name':       '=Sheet1!$A$27',
            'categories': '=Sheet1!$A$28:$A$39',
            'values':     '=Sheet1!$A$28:$A$39',
        })

        chart3.add_series({
            'name':       '=Sheet1!$B$27',
            'categories': '=Sheet1!$B$28:$B$39',
            'values':     '=Sheet1!$B$28:$B$39',
        })

        chart3.add_series({
            'name':       '=Sheet1!$C$27',
            'categories': '=Sheet1!$C$28:$C$39',
            'values':     '=Sheet1!$C$28:$C$39',
        })
        worksheet.insert_chart("G27", chart3, {'x_offset': 25, 'y_offset': 10})

        offset = 43
        for cname, cvalues in self.statistics['criterias'].items():
            for v in cvalues:
                offset += 1
                worksheet.write("A%i" % offset, cname)
                worksheet.write("B%i" % offset, v.name)
                worksheet.write("C%i" % offset, v.amount)


        offset += 2
        worksheet.write("A%i" % offset, "Question")
        worksheet.write("B%i" % offset, "Average")
        
        for avg in self.statistics['per_question_averages']:
            offset += 1
            worksheet.write("A%i" % offset, avg.title)
            worksheet.write("B%i" % offset, avg.average)

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

    template = uvclight.get_template('cr.pt', __file__)

    def jsonify(self, da):
        return json.dumps(da)

    def update(self, stats, general_stats=None):
        hs.need()
        self.stats = stats
        self.general_stats = general_stats


class SR(uvclight.Page):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        quizz = getUtility(IQuizz, self.context.course.quizz_type)
        filters = get_filters(self.request)
        stats = SessionStatistics(quizz, self.context)
        stats.update(filters)

        if 'criterias' in filters:
            general_stats = SessionStatistics(quizz, self.context)
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
            general_stats = CourseStatistics(quizz, self.context)
            general_stats.update({})
        else:
            general_stats = None

        self.charts = getMultiAdapter(
            (quizz, self.request), IView, name="charts")
        self.charts.update(stats, general_stats)

    def render(self):
        return self.charts.render()


class Excel(uvclight.Page):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        filters = get_filters(self.request)
        self.stats = SessionXSLX(quizz, self.context)
        self.stats.update(filters)

    def render(self):
        return self.stats.render()

    def make_response(self, result):
        response = self.responseFactory()
        response.headers['Content-Type'] = (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response.headers['Content-Disposition'] = (
            u'attachment; filename="output.xlsx"')

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
