# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from os import path
from zope import interface
from tempfile import TemporaryFile

from pyPdf import PdfFileWriter, PdfFileReader
from BeautifulSoup import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak
from zope.component import getUtility
from nva.psyquizz.models import IQuizz


HINWEIS = """ <b>Hinweis</b> 
Bitte beantworten Sie alle Fragen und setzen Sie pro Frage nur ein Kreuz. 
Fehlerhafte Fragebögen können leider nicht ausgewertet werden. <br/> <br/> """


class DownloadCourse(uvclight.View):
    uvclight.name('paper.pdf')
    uvclight.auth.require('zope.Public')
    uvclight.context(interface.Interface)

    heading = u"Gemeinsam zu gesunden Arbeitsbedingungen"
    base_pdf = "kfza.pdf"

    def make_response(self, result):
        response = self.responseFactory(app_iter=result)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; \
                filename="Papierfragebogen.pdf"'
        return response

    def genStuff(self, items):
        rc = []
        for item in items:
            if item:
                rc.append('[ ] %s &nbsp; &nbsp;' % item)
        return ''.join(rc)

    def update(self):
        util = getUtility(IQuizz, name=self.context.quizz_type)
        self.heading = util.__title__
        self.base_pdf = util.__base_pdf__

    def generate_page_one(self):
        style = getSampleStyleSheet()
        nm = style['Normal']
        nm.leading = 14
        story = []
        na = self.context.about.replace('\r\n', '<br/>').replace('</p>', '</p><br/>')
        bs = BeautifulSoup(na)
        doc = bs.prettify()
        story.append(Paragraph(self.heading, style['Heading2']))
        story.append(Paragraph(doc, nm))
        story.append(Paragraph(HINWEIS, style['Normal']))
        if self.context.course.criterias:
            story.append(Paragraph('<b>Bitte kreuzen Sie das zutreffende an </b>', style['Normal']))
            for crit in self.context.course.criterias:
                story.append(Paragraph('<b> %s </b> <br/> %s ' % (crit.title, self.genStuff(crit.items.split('\n'))), style['Normal']))
                #story.append(Paragraph(self.genStuff(crit.items.split('\n')), style['Normal']))
        tf = TemporaryFile()
        pdf = SimpleDocTemplate(tf, pagesize=A4)
        pdf.build(story)
        return tf

    def render(self):
        output = PdfFileWriter()
        if self.context.course.criterias:
            p1 = PdfFileReader(self.generate_page_one())
            output.addPage(p1.getPage(0))
        bpdf = "%s/%s" % (path.dirname(__file__), self.base_pdf)
        with open(bpdf, 'rb') as pdf:
            pf = PdfFileReader(pdf)
            if pf.isEncrypted:
                pf.decrypt('')
            for page in range(pf.getNumPages()):
                output.addPage(pf.getPage(page))
            ntf = TemporaryFile()
            output.write(ntf)
        ntf.seek(0)
        return ntf
