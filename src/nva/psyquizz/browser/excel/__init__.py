# -*- coding: utf-8 -*-

import os.path
import json
import uvclight
import cStringIO
import shutil
import datetime
import xlsxwriter
from backports import tempfile

from grokcore.component import name
from uvclight.auth import require
from zope.component import getUtility
from zope.schema import getFieldsInOrder

from nva.psyquizz.browser.results import (
    get_filters, CourseStatistics, SessionStatistics)
from nva.psyquizz.interfaces import ICompanyRequest
from nva.psyquizz.models import IQuizz, IClassSession


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

        if self.statistics['extra_data']:
            line = 0
            worksheet = workbook.add_worksheet('Zusatzfragen')
            for key, value in self.statistics['extra_data'].items():
                worksheet.write(line, 0, key)
                col = 0
                for question, answer in value.items():
                    worksheet.write(line + 1, col, question)
                    worksheet.write(line + 2, col, answer)
                    col += 1
                line += 5
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
