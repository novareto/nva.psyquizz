# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import os.path
import uvclight
import binascii
import base64
import qrcode
import itertools
import xlsxwriter
import cStringIO
import shutil

from backports import tempfile
from cStringIO import StringIO
from nva.psyquizz.models import IClassSession
from ..interfaces import ICompanyRequest
from ..models import ClassSession
from uvclight import Page, View
from uvclight import layer, context
from uvclight.auth import require
from uvclight import get_template
from .. import clipboard_js
from nva.psyquizz import wysiwyg
from dolmen.forms.base.datamanagers import DictDataManager
from dolmen.forms.base import FAILURE
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, PageBreak
from tempfile import TemporaryFile
from dolmen.forms.base.actions import Action, Actions
from zope.interface import Interface
from zope.schema import Text
from cromlech.browser.interfaces import IResponse
from cromlech.browser.exceptions import HTTPRedirect
from cromlech.browser.utils import redirect_exception_response
from BeautifulSoup import BeautifulSoup
from nva.psyquizz.models.interfaces import v_about


CHUNK = 4096


class ExampleText(Page):
    context(ClassSession)
    layer(ICompanyRequest)
    require('manage.company')

    @property
    def template(self):
        template = "example_text.pt"
        if self.context.strategy == "fixed":
            template = "example_text_fixed.pt"
        return get_template(template, __file__)

    def update(self):
        clipboard_js.need()
        Page.update(self)

    def generic_id(self, id):
        return binascii.hexlify(base64.urlsafe_b64encode(str(id) + ' complexificator'))


class QRLink(View):
    context(ClassSession)
    layer(ICompanyRequest)
    require('manage.company')

    def generic_id(self, id):
        return binascii.hexlify(base64.urlsafe_b64encode(str(id) + ' complexificator'))

    def render(self):
        url = '%s/befragung/generic-%s' % (
            self.application_url(), self.generic_id(self.context.id))
        img = qrcode.make(url)

        output = StringIO()
        img.save(output, format="PNG")
        output.seek(0)
        return output

    def make_response(self, result):
        response = self.responseFactory(app_iter=result)
        response.headers['Content-Type'] = 'image/png'
        response.headers['Content-Disposition'] = (
            'attachment; filename="qrcode.png"')
        return response


DOKU_TEXT = u"""Falls Sie die Kennwörter nicht mit Hilfe des Serienbriefes verteilen möchten können
Sie diese Excel Liste für eine alternative Form der Verteilung nutzen, z.B. Serien E-
Mail (Funktion ist nicht Bestandteil des Online Tools) nutzen.
Unter „Kennwörter“ finden Sie eine Übersicht der für den Zugang zur Befragung
benötigten Kennwörter. Unter „Links & Kennwörter“ sind Link und individuelles
Kennwort zusammengeführt, so dass sich nach Klick auf den Link direkt der
Fragebogen öffnen lässt."""


class DownloadTokens(uvclight.View):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        app_url = self.application_url()
        _all = itertools.chain(
            self.context.uncomplete, self.context.complete)
        self.tokens = ['%s/befragung/%s' % (app_url, a.access) for a in _all]

    def generateXLSX(self, folder, filename="ouput.xlsx"):
        filepath = os.path.join(folder, filename)
        workbook = xlsxwriter.Workbook(filepath)
        worksheet = workbook.add_worksheet(u'Dokumentation')
        worksheet.insert_textbox(0, 0, DOKU_TEXT, {'width': 450, 'height': 700, 'font': {'size': 13}})
        worksheet = workbook.add_worksheet(u'Kennwörter')
        for i, x in enumerate(self.tokens):
            worksheet.write(i, 0, x.split('/')[-1:][0])
        worksheet = workbook.add_worksheet(u'Links & Kennwörter')
        for i, x in enumerate(self.tokens):
            worksheet.write(i, 0, x)

        workbook.close()
        return filepath

    def render(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = self.generateXLSX(temp_dir)
            output = cStringIO.StringIO()
            with open(filepath, 'rb') as fd:
                shutil.copyfileobj(fd, output)
            output.seek(0)
        return output

    def make_response(self, result):
        response = self.responseFactory()
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = (
            u'attachment; filename="Kennwortliste.xlsx"')

        def filebody(r):
            data = r.read(CHUNK)
            while data:
                yield data
                data = r.read(CHUNK)

        response.app_iter = filebody(result)
        return response


class GenerateLetter(Action):

    def generate(self, tokens, text, form):
        style = getSampleStyleSheet()
        nm = style['Normal']
        nm.leading = 14
        story = []
        na = text.replace('\r\n', '<br/>').replace('</p>', '</p><br/>')
        bs = BeautifulSoup(na)
        doc = bs.prettify()
        for i, x in enumerate(tokens):
            story.append(Paragraph(doc, nm))
            story.append(Paragraph('Die Internetadresse lautet: <b> %s/befragung</b> <br/> Ihr Kennwort lautet: <b> %s</b> ' % (form.application_url(), x), nm))
            story.append(PageBreak())
        tf = TemporaryFile()
        pdf = SimpleDocTemplate(tf, pagesize=A4)
        pdf.build(story)
        tf.seek(0)
        return tf

    def tokens(self, form):
        _all = itertools.chain(
            form.context.complete, form.context.uncomplete)
        return ['%s' % (a.access) for a in _all]

    def __call__(self, form):
        data, errors = form.extractData()
        if errors:
            form.flash(u"Es ist ein Fehler aufgetreten")
            return FAILURE

        tokens = self.tokens(form)
        data = self.generate(tokens, data['text'] + '<br />', form)
        response = form.responseFactory(app_iter=data)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; \
                filename="serienbrief.pdf"'
        return response


DEFAULT = u"""
<p><b>Liebe Kolleginnen und Kollegen, </b></p>
<p>wie bereits angekündigt, erhalten Sie heute Ihre Einladung zur Teilnahme an unserer Befragung „Gut gestaltete Arbeitsbedingungen“.</p>
<p>Ziel der Befragung ist es, Ihre Arbeitsbedingungen zu beurteilen und ggf.
entsprechende Verbesserungsmaßnahmen einleiten zu können. Bitte beantworten Sie
alle Fragen offen und ehrlich. Wir sichern Ihnen vollständige Vertraulichkeit
zu. Die Ergebnisse der einzelnen Fragebögen bleiben absolut anonym. Die
Auswertung der Ergebnisse erfolgt automatisiert über unsere
Berufsgenossenschaft Elektro, Textil, Energie und Medienerzeugnisse.</p>
<p> Keine Mitarbeiterin und kein Mitarbeiter unserer Firma wird Einblick in die originalen Datensätze erhalten, eine Rückverfolgung wird nicht möglich sein.</p>
<p>Die Aussagekraft der Ergebnisse hängt von einer möglichst hohen Beteiligung ab. Geben Sie Ihrer Meinung Gewicht!</p>
<p>Die Befragung läuft vom %s - %s. Während dieses Zeitraums haben Sie die
Möglichkeit, über  die unten genannte Internetadresse an unserer Befragung
teilzunehmen. Über den Link gelangen Sie nach Eingabe des Kennwortes direkt auf
den Fragebogen unseres Unternehmens. Das Ausfüllen wird etwa 5 Minuten in
Anspruch nehmen. Nehmen Sie sich diese Zeit, Ihre Meinung zu äußern, wir freuen
uns auf Ihre Rückmeldung und bedanken uns bei Ihnen für Ihre Mitarbeit! </p>

<p>Sollten Sie Fragen oder Anmerkungen haben, wenden Sie sich bitte an:</p> <p><span> A n s p r e c h p a r t n e r   &nbsp;    und   &nbsp;     K o n t a k t d a t e n </span></p>
"""


class ILetter(Interface):
    text = Text(title=u" ", required=True, constraint=v_about)


DESC = u"""Nutzen Sie die folgende (anpassbaren) Vorlage, um Ihre Beschäftigten über die Befragung zu informieren.
Über die Funktion „Serienbrief erstellen“, wird eine PDF Datei mit Anschreiben für jeden
Beschäftigten - <b> inkl. Link zur Befragung und einem individuellen Kennwort </b> - erzeugt. Drucken
Sie die Anschreiben aus und verteilen Sie diese an die Beschäftigten.
"""




class DownloadLetter(uvclight.Form):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)
    label = u"Serienbrief"
    description = DESC

    fields = uvclight.Fields(ILetter)
    actions = Actions(GenerateLetter('Serienbrief erstellen'))
    ignoreContent = False

    def update(self):
        DE = DEFAULT % (
            self.context.startdate.strftime('%d.%m.%Y'),
            self.context.enddate.strftime('%d.%m.%Y'),
            )
        defaults = dict(text=DE)
        self.setContentData(
            DictDataManager(defaults))

    def updateForm(self):
        wysiwyg.need()
        action, result = self.updateActions()
        if IResponse.providedBy(result):
            return result
        self.updateWidgets()

    def __call__(self, *args, **kwargs):
        try:
            self.update(*args, **kwargs)
            response = self.updateForm()
            if response is not None:
                return response
            result = self.render(*args, **kwargs)
            return self.make_response(result, *args, **kwargs)
        except HTTPRedirect, exc:
            return redirect_exception_response(self.responseFactory, exc)
