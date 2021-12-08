# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight
import datetime
from tempfile import TemporaryFile
from BeautifulSoup import BeautifulSoup
from pyPdf import PdfFileWriter, PdfFileReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Spacer, PageBreak, Paragraph, SimpleDocTemplate
from reportlab.lib.units import cm

from zope import interface
from zope.component import getUtility
from zope.component.hooks import getSite
from dolmen.forms.base.actions import Actions
from uvclight import Form
from nva.psyquizz.browser.forms import AnswerQuizz, CompanyAnswerQuizz
from nva.psyquizz.models import IQuizz
from ..extra_questions import generate_extra_questions
from ..i18n import _
from ..interfaces import ICompanyRequest
from ..models import IClassSession


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

    def genStuffFQ(self, source):
        rc = []
        for item in source:
            if item:
                rc.append('[ ] %s &nbsp; &nbsp;' % item.title)
        return ''.join(rc)

    def update(self):
        util = getUtility(IQuizz, name=self.context.quizz_type)
        self.heading = util.__title__
        self.base_pdf = util.__base_pdf__

    def generate_page_one(self):
        def clean(tag, whitelist=[]):
            tag.attrs = None
            for e in tag.findAll(True):
                for attribute in e.attrs:
                    if attribute[0] in whitelist:
                        del e[attribute[0]]
                e.attrs = None
            return tag
        style = getSampleStyleSheet()
        nm = style['Normal']
        nm.leading = 14
        story = [Spacer(0, 2*cm)]
        na = self.context.about.replace('\r\n', '<br/>').replace('</p>', '</p><br/>')
        bs = BeautifulSoup(na)
        clean(bs, ['style', 'face'])
        doc = bs.prettify()
        story.append(Paragraph(self.heading, style['Heading2']))
        story.append(Paragraph(doc, nm))
        story.append(Paragraph(HINWEIS, style['Normal']))
        from zope.schema._field import Set
        if self.context.course.criterias:
            story.append(Paragraph('<b>Bitte kreuzen Sie das zutreffende an </b>', style['Normal']))
            for crit in self.context.course.criterias:
                story.append(Paragraph('<b> %s </b> <br/> %s ' % (crit.title, self.genStuff(crit.items.split('\n'))), style['Normal']))

        if self.context.course.fixed_extra_questions:
            from zope.schema import getFieldsInOrder
            story.append(PageBreak())
            quizz = getUtility(IQuizz, name=self.context.quizz_type)
            for iface in quizz.additional_extra_fields(self.context.course):
                story.append(Paragraph('<br/><br/><b>%s </b>' % iface.__doc__, style['Normal']))
                for name, field in getFieldsInOrder(iface):
                    story.append(Paragraph('<b> %s </b> <br/> %s ' % (field.description, self.genStuffFQ(field.source)), style['Normal']))

        if self.context.course.extra_questions:
            story.append(PageBreak())
            story.append(Paragraph('<br/><br/><b>Zusatzfragen: </b>', style['Normal']))
            for field in generate_extra_questions( self.context.course.extra_questions):
                if isinstance(field, Set):
                    story.append(Paragraph(u'<br/><b> %s </b> <br/>%s (Mehrere Antworten möglich) <br/> <br/>' %
                        (field.description, self.genStuff([x.title for x in field.value_type.source])), style['Normal']))
                else:
                    story.append(Paragraph('<b> %s </b> <br/> %s' %
                        (field.description, self.genStuff([x.title for x in field.source])), style['Normal']))
        tf = TemporaryFile()
        pdf = SimpleDocTemplate(tf, pagesize=A4)
        pdf.build(story)
        return tf

    def render(self):
        output = PdfFileWriter()
        resources = getSite().configuration.resources
        base1 = resources.get("kfza_base.pdf")
        base1 = open(base1, 'rb')
        b1_pdf = PdfFileReader(base1)
        wm = b1_pdf.getPage(0)
        p1 = PdfFileReader(self.generate_page_one())

        for num in range(p1.numPages-1):
            page1 = p1.getPage(num + 1)
            page1.mergePage(wm)
            output.addPage(page1)

        page1 = p1.getPage(0)
        page1.mergePage(wm)
        output.addPage(page1)
        bpdf = resources.get(self.base_pdf)
        with open(bpdf, 'rb') as pdf:
            pf = PdfFileReader(pdf)
            if pf.isEncrypted:
                pf.decrypt('')
            for page in range(pf.getNumPages()):
                output.addPage(pf.getPage(page))
            if self.context.course.extra_questions or self.context.course.fixed_extra_questions:
                b1_pdf = PdfFileReader(base1)
                wm = b1_pdf.getPage(0)
                p1 = PdfFileReader(self.generate_page_one())
                for num in range(p1.numPages-1):
                    page1 = p1.getPage(num + 1)
                    page1.mergePage(wm)
                    output.addPage(page1)
            ntf = TemporaryFile()
            output.write(ntf)
        ntf.seek(0)
        base1.close()
        return ntf


class GenericAnswerQuizz(AnswerQuizz):
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)
    uvclight.name('answer')
    uvclight.auth.require('manage.company')
    uvclight.title(_(u'Answer the quizz'))
    dataValidators = []
    label = u"Eingabe Papierfragebögen"
    description = u"Eingabe kann per DropDown Menü oder über die Tastatur (Kreuz ganz links Eingabe 1 bis Kreuz ganz rechts Eingabe 5) erfolgen."

    fmode = 'input'
    actions = Actions(CompanyAnswerQuizz(u'speichern'))

    def update(self):
        self.template = Form.template
        course = self.context.course
        self.quizz = getUtility(IQuizz, name=course.quizz_type)
        startdate = self.context.startdate
        if datetime.date.today() < startdate:
            self.flash(u'Die Befragung beginnt erst am %s deshalb werden Ihre Ergebnisse nicht gespeichert' % startdate.strftime('%d.%m.%Y'))
        Form.update(self)

    @property
    def action_url(self):
        return self.request.url

    def render(self):
        form = Form.render(self)
        jscontent = u"""
<style>
   label {  float: left; padding-right: 20px; }
   .highlight {
     background-color: #f7dada;
   }
</style>
<script type="text/javascript">
   $(document).ready(function() {
        $('select').each(function(sidx) {
           $('option', $(this)).each(function(oidx) {
              $(this).html((oidx + 1).toString() + ' - ' + $(this).html());
           });
           $(this).prepend("<option value=''></option>").val('');
           $(this).bind('keypress',function(e) {
              if (e.which === 49) {
                  $(this).val($('select:nth-child(2)', $(this)).val());
              } else if (e.which === 50) {
                  $(this).val($('select:nth-child(3)', $(this)).val());
              } else if (e.which === 51) {
                  $(this).val($('select:nth-child(4)', $(this)).val());
              } else if (e.which === 52) {
                  $(this).val($('select:nth-child(5)', $(this)).val());
              } else if (e.which === 53) {
                  $(this).val($('select:nth-child(6)', $(this)).val());
              }
           });
        });

        $('select').first().focus();

        $("form").submit(function(){
            var isFormValid = true;
            $("select").each(function() {
               if ($.trim($(this).val()).length == 0) {
                  $(this).parent().addClass("highlight");
                  isFormValid = false;
               } else {
                  $(this).parent().removeClass("highlight");
               }
            });
            if (!isFormValid) {
                alert("Bitte füllen Sie zunächst alle Felder. Im Anschluss können Sie das Formular absenden.");
            }
            return isFormValid;
        });
   });
</script>
"""
        return jscontent + form
