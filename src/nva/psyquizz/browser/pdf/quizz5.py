# -*- coding: utf-8 -*-

import json
import uvclight
import tempfile
from svglib.svglib import svg2rlg
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph, Table, TableStyle
from nva.psyquizz.browser.pdf import GeneratePDF, styles
from nva.psyquizz.models.quizz.quizz5 import IQuizz5
from tempfile import NamedTemporaryFile


class Quizz5PDF(GeneratePDF):
    uvclight.context(IQuizz5)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def generate(self):
        parts = []
        self.frontpage(parts)
        avg = json.loads(self.request.form['averages'])
        pSVGs = self.request.form.get('pSVG')
        assert isinstance(pSVGs, list)
        i = 0
        for pSVG in pSVGs:
            tf = tempfile.NamedTemporaryFile()
            tf.write(unicode(pSVG).encode('utf-8'))
            tf.seek(0)
            drawing = svg2rlg(tf.name)
            drawing.scale(0.7, 0.7)
            parts.append(drawing)

            if i == 18:
                parts.append(PageBreak())
                parts.append(Paragraph('<h1>Umgebungsvariablen<h1>', styles['Heading1']))
                parts.append(Paragraph('<p>Im Folgenden sehen Sie die Ergebnisse der einzelnen Fragen zu den für die psychische Belastung relevanten Arbeitsumgeb      ungsfaktoren.</p>', styles['Normal']))
            i += 1

        return parts

    def render(self):
        if self.request.form.get('chart', None) == None:
            return None
        doc = SimpleDocTemplate(
            NamedTemporaryFile()) #, pagesize=landscape(letter))
        parts = self.generate()
        doc.build(
            parts, onFirstPage=self.headerfooter,
            onLaterPages=self.headerfooter
        )
        pdf = doc.filename
        pdf.seek(0)
        return pdf.read()

    def headerfooter(self, canvas, doc):
        canvas.setFont("Helvetica", 9)
        canvas.drawString(1 * cm, 2 * cm, u"Gemeinsam zu gesunden Arbeitsbedingungen")
        canvas.drawString(1 * cm, 1.6 * cm, u"Psychische Belastungen online erfassen")
        canvas.drawString(15 * cm, 2 * cm, u"Grundlage der Befragung:")
        canvas.drawString(15 * cm, 1.6 * cm, u"FBGU-Fragebogen")
        canvas.setFont("Helvetica", 12)
