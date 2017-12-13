# -*- coding: utf-8 -*-

import json
import uvclight
import tempfile

from svglib.svglib import svg2rlg


from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Table, TableStyle


from nva.psyquizz.browser.pdf import GeneratePDF, styles
from nva.psyquizz.models.quizz.quizz3 import IQuizz3


class PDF_WAI(GeneratePDF):
    uvclight.context(IQuizz3)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def headerfooter(self, canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.drawString(1 * cm, 2 * cm, u"Gemeinsam zu gesunden Arbeitsbedingungen")
        canvas.drawString(1 * cm, 1.6 * cm, u"Psychische Belastungen online erfassen")
        canvas.drawString(1 * cm, 1.2 * cm, u"Ein Programm der BG ETEM")
        if doc.page >= 3:
            canvas.drawString(18 * cm, 2 * cm, u"Grundlage der Befragung")
            canvas.drawString(18 * cm, 1.6 *cm, u"Work Ability Index (WAI)")
            canvas.drawString(18 * cm, 1.2 * cm, u"Ilmanien, Tuomi")

        else:
            canvas.drawString(18 * cm, 2 * cm, u"Grundlage der Befragung: KFZA - Kurzfragebogen")
            canvas.drawString(18 * cm, 1.6 *cm, u"zur Arbeitsanalyse")
            canvas.drawString(18 * cm, 1.2 * cm, u"Prümper, J., Hartmannsgruber, K. & Frese, M")
        canvas.line(0.5 * cm, 2.5 * cm, 26 * cm, 2.5 * cm)
        canvas.setFont("Helvetica", 12)

    def generate(self):
        parts = super(PDF_WAI, self).generate()
        parts.append(PageBreak())
        donut = self.request.form.get('donut')
        tf = tempfile.NamedTemporaryFile()
        tf.write(unicode(donut).encode('utf-8'))
        tf.seek(0)
        drawing = svg2rlg(tf.name)
        parts.append(Paragraph(u'WAI FRAGEBOGEN', styles['Heading2']))
        parts.append(drawing)
        parts.append(PageBreak())
        vp = json.loads(self.request.form.get('vp'))
        td = [[u'Summenscore', 'Anzahl Probanten']]
        for x, y in vp.items():
            td.append([x, y])
        parts.append(Paragraph(u'Summenscore pro Proband', styles['Normal']))
        table = Table(data=td)
        ts = TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ])
        table.setStyle(ts)
        parts.append(table)
        return parts
