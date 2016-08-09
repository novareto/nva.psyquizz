# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import json
import uvclight
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

styles = getSampleStyleSheet()


def read_data_uri(uri):
    ctype, data = uri.split(',', 1)
    binary_data = a2b_base64(data)
    fd = StringIO()
    fd.write(binary_data)
    fd.seek(0)
    return fd


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

    def make_response(self, result):
        response = self.responseFactory(app_iter=result)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; \
                filename="charts.pdf"'
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
        canvas.drawString(1 * cm, 20 * cm, self.context.course.company.name)
        canvas.drawString(1 * cm, 19.5 * cm, self.context.course.title)
        try:
            canvas.drawString(1 * cm, 19.0 * cm, u"Befragungszeitraum %s - %s" % (
                self.context.startdate.strftime('%d.%m.%Y'),
                self.context.enddate.strftime('%d.%m.%Y')))
        except:
            print "ERROR"
        canvas.line(0.5 * cm , 18.5 * cm, 26 * cm, 18.5 * cm)

    def render(self):
        doc = SimpleDocTemplate(
            NamedTemporaryFile(), pagesize=landscape(letter))
        parts = []
        rc = []
        criterias = dict(json.loads(self.request.form['criterias']))
        for k,v in criterias.items():
            rc.append(
                "<li> %s: %s </li>" %(k, v)
                )
        if not rc:
            rc.append('alle')
        crit_style = "<ul> %s </ul>" % "".join(rc)

        avg = json.loads(self.request.form['averages'])

        chart = read_data_uri(self.request.form['chart'])
        userschart = read_data_uri(self.request.form['userschart'])
        parts.append(Spacer(0, 2*cm))
        parts.append(Paragraph(u'Anzahl Fragebögen %s' % self.request.form['total'], styles['Normal']))
        parts.append(Paragraph(u'Auswertungsgruppe', styles['Normal']))
        parts.append(Paragraph(crit_style, styles['Normal']))
        image = Image(chart, width=650, height=650, kind='proportional')
        parts.append(image)
        parts.append(Paragraph(LEGEND, styles['Normal']))
        parts.append(PageBreak())
        parts.append(Spacer(0, 4*cm))
        parts.append(Paragraph(u'Mittelwerte', styles['Normal']))

        table = Table(data=[[k, v] for k, v in avg.items()])
        ts = TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ])
        table.setStyle(ts)
        parts.append(table)
        parts.append(PageBreak())
        parts.append(Spacer(0, 1*cm))
        parts.append(Paragraph(u'Verteilung der Antworten', styles['Normal']))
        parts.append(Image(userschart, width=500, height=400))

        doc.build(parts, onFirstPage=self.headerfooter, onLaterPages=self.headerfooter)
        pdf = doc.filename
        pdf.seek(0)
        return pdf.read()
