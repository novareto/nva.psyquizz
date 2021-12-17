# -*- coding: utf-8 -*-

import json
import uvclight
import tempfile
from svglib.svglib import svg2rlg
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Table, TableStyle
from nva.psyquizz.browser.pdf import GeneratePDF, styles
from nva.psyquizz.models.quizz.quizz5 import IQuizz5


class PDF_WAI(GeneratePDF):
    uvclight.context(IQuizz5)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def generate(self):
        parts = []
        avg = json.loads(self.request.form['averages'])
        pSVGs = self.request.form.get('pSVG')
        assert isinstance(pSVGs, list)

        for pSVG in pSVGs:
            tf = tempfile.NamedTemporaryFile()
            tf.write(unicode(pSVG).encode('utf-8'))
            tf.seek(0)
            drawing = svg2rlg(tf.name)
            drawing.height = 100.0
            drawing.width = 600.0
            parts.append(drawing)

        return parts
