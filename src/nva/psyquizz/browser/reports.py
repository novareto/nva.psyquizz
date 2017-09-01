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

class PDFView(uvclight.View):
    uvclight.baseclass()
    
    def make_response(self, result):
        response = self.responseFactory(app_iter=result)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; \
                filename="Resultate_Befragung.pdf"'
        return response


class GeneratePDF(PDFView):
    uvclight.baseclass()
    uvclight.context(Interface)
    uvclight.name('pdf')
    uvclight.auth.require('zope.Public')

    def crit_style(self):
        if int(self.request.form.get('has_criterias', 0)) > 0:
            rc = []
            criterias = dict(json.loads(self.request.form['criterias']))
            for k,v in criterias.items():
                rc.append(
                    "<li> %s: %s </li>" %(k, v)
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
            self.request.form['total'],
            crit_style,
            datetime.datetime.now().strftime('%d.%m.%Y'))
        parts.append(Paragraph(fp.strip(), styles['Normal']))
        parts.append(PageBreak())
        return 
