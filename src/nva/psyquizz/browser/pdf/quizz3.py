# -*- coding: utf-8 -*-

import uvclight
import tempfile

from reportlab.platypus import PageBreak, Paragraph
from svglib.svglib import svg2rlg

from nva.psyquizz.browser.pdf import GeneratePDF, styles
from nva.psyquizz.models.quizz.quizz3 import IQuizz3


class PDF_WAI(GeneratePDF):
    uvclight.context(IQuizz3)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def generate(self):
        parts = super(PDF_WAI, self).generate()
        parts.append(PageBreak())
        donut = self.request.form.get('donut')
        tf = tempfile.NamedTemporaryFile()
        tf.write(unicode(donut).encode('utf-8'))
        tf.seek(0)
        drawing = svg2rlg(tf.name)
        parts.append(Paragraph(u'WAI FRAGEBOGEN', styles['Normal']))
        parts.append(drawing)
        return parts
