# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import json
import uvclight
import datetime
import tempfile

from cStringIO import StringIO
from zope.interface import Interface
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import (SimpleDocTemplate, PageBreak, Image,
        Paragraph, Table, TableStyle, Spacer)
from reportlab.lib.styles import getSampleStyleSheet
from tempfile import NamedTemporaryFile
from binascii import a2b_base64
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from svglib.svglib import svg2rlg

from nva.psyquizz.models.quizz.quizz2 import IQuizz2
from nva.psyquizz.models.quizz.quizz1 import IQuizz1

styles = getSampleStyleSheet()


def read_data_uri(uri):
    ctype, data = uri.split(',', 1)
    binary_data = a2b_base64(data)
    fd = StringIO()
    fd.write(binary_data)
    fd.seek(0)
    return fd


FRONTPAGE = u"""
%s<br/>
%s <br/>
Befragungszeitraum: %s – %s <br/> <br/>
<u>Grundlage der Ergebnisse</u> <br/>
Auswertungsgruppe: %s <br/>
Anzahl Fragebögen: %s <br/>
Auswertung erzeugt: %s <br/>
"""

LEGEND = """
    <em><font color="#62B645"><b> > 3,5: </b></font> in diesem Bereich scheint alles in Ordnung</em><br/>
    <em><font color="#FFCC00"><b> > 2,5 < 3,5: </b></font> diesen Bereich sollten Sie sich noch mal genauer ansehen</em><br/>
    <em><font color="#D8262B"><b> < 2,5:  </b> </font> in diesem Bereich scheint Handlungsbedarf zu bestehen </em>
  </div>
"""

class GeneratePDF(uvclight.Page):
    uvclight.context(Interface)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def crit_style(self):
        if int(self.request.form.get('has_criterias', 0)) > 0:
            rc = []
            criterias = json.loads(self.request.form.get('criterias', {}))
            for k, v in criterias.items():
                rc.append(
                    "<li> %s </li>" %(v[1])
                    )
            if not rc:
                rc.append('alle')
        else:
            rc = ['alle']

        crit_style = "<ul> %s </ul>" % "".join(rc)
        return crit_style

    def frontpage(self, parts):
        crit_style = self.crit_style()
        parts.append(Paragraph(u'Auswertungsbericht', styles['Heading1']))
        parts.append(Paragraph(u'„Gemeinsam zu gesunden Arbeitsbedingungen“ – Psychische Belastung erfassen', styles['Heading2']))
        fp = FRONTPAGE % (
            self.context.course.company.name, 
            self.context.course.title, 
            self.context.startdate.strftime('%d.%m.%Y'), 
            self.context.enddate.strftime('%d.%m.%Y'),
            crit_style,
            self.request.form['total'],
            datetime.datetime.now().strftime('%d.%m.%Y'))
        parts.append(Paragraph(fp.strip(), styles['Normal']))
        parts.append(PageBreak())
        return 

    def make_response(self, result):
        response = self.responseFactory(app_iter=result)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; \
                filename="Resultate_Befragung.pdf"'
        return response

    def headerfooter(self, canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.drawString(1 * cm, 2 * cm, u"Gemeinsam zu gesunden Arbeitsbedingungen")
        canvas.drawString(1 * cm, 1.6 * cm, u"Psychische Belastungen online erfassen")
        canvas.drawString(1 * cm, 1.2 * cm, u"Ein Programm der BG ETEM")
        canvas.drawString(18 * cm, 2 * cm, u"Grundlage der Befragung: KFZA - Kurzfragebogen")
        canvas.drawString(18 * cm, 1.6 *cm, u"zur Arbeitsanalyse")
        canvas.drawString(18 * cm, 1.2 * cm, u"Prümper, J., Hartmannsgruber, K. & Frese, M")
        canvas.line(0.5 * cm , 2.5 * cm, 26 * cm, 2.5 * cm)
        canvas.setFont("Helvetica", 12)
        #canvas.drawString(1 * cm, 20 * cm, self.context.course.company.name)
        #canvas.drawString(1 * cm, 19.5 * cm, self.context.course.title)
        #try:
        #    canvas.drawString(1 * cm, 19.0 * cm, u"Befragungszeitraum %s - %s" % (
        #        self.context.startdate.strftime('%d.%m.%Y'),
        #        self.context.enddate.strftime('%d.%m.%Y')))
        #except:
        #    print "ERROR"
        #canvas.line(0.5 * cm , 18.5 * cm, 26 * cm, 18.5 * cm)

    def render(self):
        doc = SimpleDocTemplate(
            NamedTemporaryFile(), pagesize=landscape(letter))
        parts = []
        avg = json.loads(self.request.form['averages'])
        #chart = read_data_uri(self.request.form['chart'])
        #userschart = read_data_uri(self.request.form['userschart'])
        pSVG = self.request.form.get('pSVG')
        tf = tempfile.NamedTemporaryFile()
        tf.write(unicode(pSVG).encode('utf-8'))
        tf.seek(0)
        drawing = svg2rlg(tf.name)
        drawing.height = 350.0
        pSVG1 = self.request.form.get('pSVG1')
        tf = tempfile.NamedTemporaryFile()
        tf.write(unicode(pSVG1).encode('utf-8'))
        tf.seek(0)
        drawing1 = svg2rlg(tf.name)
        ## Page1
        self.frontpage(parts)
        ## Page2
        parts.append(drawing)
        parts.append(Paragraph(LEGEND, styles['Normal']))
        parts.append(PageBreak())
        parts.append(Paragraph(u'Mittelwerte', styles['Normal']))

        table = Table(data=avg)
        ts = TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ])
        table.setStyle(ts)
        parts.append(table)
        parts.append(PageBreak())
        parts.append(Spacer(0, 1*cm))
        parts.append(drawing1)
        doc.build(parts, onFirstPage=self.headerfooter, onLaterPages=self.headerfooter)
        pdf = doc.filename
        pdf.seek(0)
        return pdf.read()


class PDFPL(GeneratePDF):
    uvclight.context(IQuizz1)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def headerfooter(self, canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.drawString(1 * cm, 2 * cm, u"Gemeinsam zu gesunden Arbeitsbedingungen")
        canvas.drawString(1 * cm, 1.6 * cm, u"Psychische Belastungen online erfassen")
        canvas.drawString(1 * cm, 1.2 * cm, u"Ein Programm der BG ETEM")
        canvas.drawString(18 * cm, 2 * cm, u"Grundlage der Befragung:  Prüfliste Psychische")
        canvas.drawString(18 * cm, 1.6 *cm, u"Belastung")
        canvas.drawString(18 * cm, 1.2 * cm, u"Unfallversicherung Bund und Bahn")
        canvas.line(0.5 * cm , 2.5 * cm, 26 * cm, 2.5 * cm)
        #canvas.setFont("Helvetica", 12)
        #canvas.drawString(1 * cm, 20 * cm, self.context.course.company.name)
        #canvas.drawString(1 * cm, 19.5 * cm, self.context.course.title)
        #try:
        #    canvas.drawString(1 * cm, 19.0 * cm, u"Befragungszeitraum %s - %s" % (
        #        self.context.startdate.strftime('%d.%m.%Y'),
        #        self.context.enddate.strftime('%d.%m.%Y')))
        #except:
        #    print "ERROR"
        #canvas.line(0.5 * cm , 18.5 * cm, 26 * cm, 18.5 * cm)

    def render(self):
        doc = SimpleDocTemplate(
            NamedTemporaryFile(), pagesize=landscape(letter))
        parts = []
        pSVG = self.request.form.get('pSVG1')
        tf = tempfile.NamedTemporaryFile()
        tf.write(unicode(pSVG).encode('utf-8'))
        tf.seek(0)
        drawing = svg2rlg(tf.name)
        #drawing.width = 40.0
        drawing.renderScale = 0.57
        ## Page1
        self.frontpage(parts)
        #parts.append(Spacer(0, 0.2*cm))
        parts.append(drawing)
        doc.build(parts, onFirstPage=self.headerfooter, onLaterPages=self.headerfooter)
        pdf = doc.filename
        pdf.seek(0)
        return pdf.read()
