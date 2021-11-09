# -*- coding: utf-8 -*-

import uvclight
import tempfile

from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate
from tempfile import NamedTemporaryFile
from reportlab.lib.units import cm
from svglib.svglib import svg2rlg

from nva.psyquizz.browser.pdf import GeneratePDF
from nva.psyquizz.models.quizz.quizz1 import IQuizz1


class PDFPL(GeneratePDF):
    uvclight.context(IQuizz1)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def headerfooter(self, canvas, doc):
        canvas.setFont("Helvetica", 9)

        canvas.drawString(
            1 * cm, 2 * cm, u"Gemeinsam zu gesunden Arbeitsbedingungen")
        canvas.drawString(
            1 * cm, 1.6 * cm, u"Psychische Belastungen online erfassen")
        canvas.drawString(
            1 * cm, 1.2 * cm, u"Ein Programm der VBG")
        canvas.drawString(
            18 * cm, 2 * cm, u"Grundlage der Befragung:  Prüfliste Psychische")
        canvas.drawString(
            18 * cm, 1.6 *cm, u"Belastung")
        canvas.drawString(
            18 * cm, 1.2 * cm, u"Unfallversicherung Bund und Bahn")

        canvas.line(0.5 * cm , 2.5 * cm, 26 * cm, 2.5 * cm)

    def render(self):
        doc = SimpleDocTemplate(
            NamedTemporaryFile(), pagesize=landscape(letter))
        parts = []
        pSVG = self.request.form.get('pSVG1')
        tf = tempfile.NamedTemporaryFile()
        tf.write(unicode(pSVG).encode('utf-8'))
        tf.seek(0)
        drawing = svg2rlg(tf.name)        
        drawing.renderScale = 0.57

        self.frontpage(parts)
        parts.append(drawing)
        doc.build(parts, onFirstPage=self.headerfooter,
                  onLaterPages=self.headerfooter)
        pdf = doc.filename
        pdf.seek(0)
        return pdf.read()
