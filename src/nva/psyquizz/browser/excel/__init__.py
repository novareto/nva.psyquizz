# -*- coding: utf-8 -*-

import os.path
import json
import uvclight
import cStringIO
import shutil
import datetime
import xlsxwriter
from backports import tempfile

from zope.component import getUtility, queryUtility
from zope.schema import getFieldsInOrder
from zope.interface import Interface
from grokcore.component import name
from cromlech.sqlalchemy import get_session
from cromlech.browser import exceptions
from uvclight.auth import require
from uvclight.utils import current_principal

from nva.psyquizz.browser.results import (
    get_filters, CourseStatistics, SessionStatistics)
from nva.psyquizz.interfaces import ICompanyRequest
from nva.psyquizz.models import IQuizz, IClassSession, Company


CHUNK = 4096


FRONTPAGE = u"""
Auswertungsbericht
„Gemeinsam zu gesunden Arbeitsbedingungen“ – Psychische Belastung erfassen
%s
%s

Befragungszeitraum: %s – %s
Grundlage der Ergebnisse
Auswertungsgruppe: %s
Anzahl Fragebögen: %s
Auswertung erzeugt: %s
"""


class XSLX(object):

    enable_chart1 = True
    enable_verteilung = True
    enable_ergebnisse = False
    enable_averages = True

    def generate_mittelwerte(self, workbook):
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

        worksheet.write(0, 0, 'Bereich')
        worksheet.write(0, 1, 'Mittelwert der Skala')
        for i, x in enumerate(self.statistics['global.averages']):
            worksheet.write(i+1, 0, x.title)
            worksheet.write(i+1, 1, x.average, nformat)

        if self.enable_chart1:
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
            worksheet.insert_chart(
                'A13', chart1, {'x_offset': 25, 'y_offset': 10})

    def generate_ergebnisse(self, workbook):
        ws = workbook.add_worksheet(u'Ergebnisse')
        total = 0
        xAxis = []
        good = dict(name="Eher Ja", data=[], abv=[], color="#62B645")
        bad = dict(name="Eher Nein", data=[], abv=[],color="#D8262B")

        averages = self.quizz.__schema__.queryTaggedValue('averages')
        if averages:
            avg_labels = {}
            for label, ids in averages.items():
                avg_labels.update({id: label for id in ids})

        for key, answers in self.statistics['raw'].items():
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
            good['abv'].append(yesses)
            bad['data'].append(float(noes)/total * 100)
            bad['abv'].append(noes)
        xAxis_labels = {
            k.title: k.description for id, k in
            getFieldsInOrder(self.quizz.__schema__)}
        line = 0
        ws.write(line, 0, 'Scale')
        ws.write(line, 1, 'Frage')
        ws.write(line, 2, 'eher ja - %')
        ws.write(line, 3, 'eher ja - total')
        ws.write(line, 4, 'eher nein - %')
        ws.write(line, 5, 'eher nein - total')
        line = 1
        for idx in xAxis:
            if averages:
                ws.write(line, 0, avg_labels[idx])
            ws.write(line, 1, xAxis_labels[idx])
            ws.write(line, 2, "%s" %(good['data'][int(idx)-1]))
            ws.write(line, 3, "%s" %(good['abv'][int(idx)-1]))
            ws.write(line, 4, "%s" %(bad['data'][int(idx)-1]))
            ws.write(line, 5, "%s" %(bad['abv'][int(idx)-1]))

            line += 1

    def generateXLSX(self, workbook):
        #filepath = os.path.join(folder, filename)
        #workbook = xlsxwriter.Workbook(filepath)
        worksheet0 = workbook.add_worksheet('Dokumentation')
        amounts = dict(json.loads(self.json_criterias))
        db = ""
        if len(self.filters.get('criterias', {})) == 0:
            db = "alle"
        for k,v in self.filters.get('criterias', {}).items():
            db +=  "%s %s" % (v.name, amounts.get(v.name))
        fp = FRONTPAGE % (
            self.course.company.name,
            self.course.title,
            self.session.startdate.strftime('%d.%m.%Y'),
            self.session.enddate.strftime('%d.%m.%Y'),
            db,
            self.statistics.get('total'),
            datetime.datetime.now().strftime('%d.%m.%Y'))
        #worksheet0.insert_textbox(10, 2, 'fp', {'width': 800, 'height': 300, 'font': {'size': 13}})
        fm = workbook.add_format()
        fm.set_font_size(16)
        fm.set_text_wrap()
        worksheet0.set_column(0, 0, 130)

        worksheet0.write(0, 0, fp, fm)


        amounts = dict(json.loads(self.json_criterias))
        # ii = 1
        #for k,v in self.filters.get('criterias', {}).items():
        #    worksheet.write(ii, 0,  "%s %s" % (v.name, amounts.get(v.name)))
        #    ii += 1
        self.generate_mittelwerte(workbook)


        if self.enable_verteilung:
            worksheet = workbook.add_worksheet('Verteilung')
            nformat = workbook.add_format()
            nformat.set_num_format('0.00')

            data = json.loads(self.series)
            for y, x in enumerate(data):
                name = x['name']
                r = 1
                worksheet.write(0, y, name)
                for i, z in enumerate(x['data']):
                    worksheet.write((r+1+i), y, z, nformat)

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
                'fill':   {'color': data[0]['color']},
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
                'fill':   {'color': data[2]['color']},
            })

            chart3.set_y_axis({'reverse': True})
            worksheet.insert_chart("A20", chart3, {'x_offset': 15, 'y_offset': 10})
        if self.enable_averages:
            worksheet = workbook.add_worksheet('Mittelwerte pro Frage')
            nformat = workbook.add_format()
            nformat.set_num_format('0.00')
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

        if self.enable_ergebnisse:
            self.generate_ergebnisse(workbook)

        if self.statistics['extra_data']:
            line = 0
            worksheet = workbook.add_worksheet('Zusatzfragen')
            for label, answers in self.extra_questions_order.items():
                value = self.statistics['extra_data'][label]
                worksheet.write(line, 0, label)
                col = 1
                for answer in answers:
                    worksheet.write(line + 0, col, answer)
                    worksheet.write(line + 1, col, value.get(answer, 0))
                    col += 1
                line += 4
        return workbook

    def render(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, 'ErgebnisExcel.xlsx')
            workbook = xlsxwriter.Workbook(filepath)
            workbook = self.generateXLSX(workbook)
            workbook.close()

            output = cStringIO.StringIO()
            with open(filepath, 'rb') as fd:
                shutil.copyfileobj(fd, output)

            output.seek(0)
        return output


class CourseXSLX(CourseStatistics, XSLX):
    name('xslx')


class SessionXSLX(SessionStatistics, XSLX):
    name('xslx')


class Excel(uvclight.Page):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        quizz = getUtility(IQuizz, self.context.quizz_type)
        self.stats = SessionXSLX(quizz, self.context)
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


ALLOWED_USERS = {'test@example.com'}


class SimpleExcelExport(uvclight.Page):
    require('zope.Public')
    uvclight.context(Interface)
    uvclight.layer(ICompanyRequest)

    def update(self):
        user = current_principal()
        #if not user.id in ALLOWED_USERS:
        #    raise exceptions.HTTPForbidden('Not allowed.')
        self.session = get_session('school')


    def quizz_results(self, quizz, worksheet):
        results = self.session.query(quizz).filter(
            quizz.company_id == Company.id,
            Company.exp_db == "true"
        )
        xAxis_labels = {
            k.title: k.description for id, k in
            getFieldsInOrder(quizz.__schema__)
        }

        fields = getFieldsInOrder(quizz.__schema__)
        for idx, field_info in enumerate(fields):
            qid, field = field_info
            worksheet.write(0, idx, xAxis_labels[field.title])

        for line, res in enumerate(results, 1):
            for idx, field_info in enumerate(fields):
                qid, field = field_info
                worksheet.write(line, idx, getattr(res, qid, None))
        return worksheet


    def render(self):
        quizzes = ('quizz1', 'quizz2', 'quizz3', 'quizz4', 'quizz5')
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, 'ErgebnisExcel.xlsx')
            workbook = xlsxwriter.Workbook(filepath)
            for quizz_type in quizzes:
                quizz = queryUtility(IQuizz, quizz_type)
                if quizz is not None:
                    worksheet = workbook.add_worksheet(quizz_type)
                    worksheet = self.quizz_results(quizz, worksheet)
            workbook.close()

            output = cStringIO.StringIO()
            with open(filepath, 'rb') as fd:
                shutil.copyfileobj(fd, output)

            output.seek(0)
        return output

    def make_response(self, result):
        response = self.responseFactory()
        response.headers['Content-Type'] = (
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response.headers['Content-Disposition'] = (
            u'attachment; filename="rohdaten_befragungen.xlsx"')

        def filebody(r):
            data = r.read(CHUNK)
            while data:
                yield data
                data = r.read(CHUNK)

        response.app_iter = filebody(result)
        return response
