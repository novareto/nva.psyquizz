# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import json
import uvclight
from dolmen.forms.ztk.widgets import choice, date
from dolmen.forms.ztk.widgets.collection import MultiChoiceFieldWidget
from dolmen.forms.ztk.widgets.collection import SetField
from dolmen.forms.ztk.widgets.text import TextareaWidget, TextField
from grokcore.component import adapts, name
from nva.psyquizz import efw
from nva.psyquizz.browser import forms
from nva.psyquizz.interfaces import IQuizzLayer
from uvc.themes.btwidgets.widgets.choice import RadioFieldWidget
from uvc.themes.btwidgets.widgets.date import DateFieldWidget
from zope.interface import Interface

from ..extra_questions import parse_extra_question_syntax


class DateFieldWidget(DateFieldWidget):
    adapts(date.DateField, Interface, IQuizzLayer)
    template = uvclight.get_template('datefieldwidget.cpt', __file__)


class RadioFieldWidget(RadioFieldWidget):
    name('blockradio')
    adapts(choice.ChoiceField, Interface, Interface)
    template = uvclight.get_template('radiofieldwidget.cpt', __file__)


class MultiChoiceFieldWidget(MultiChoiceFieldWidget):
    adapts(SetField, choice.ChoiceField, Interface, IQuizzLayer)
    template = uvclight.get_template('multichoicefieldwidget.cpt', __file__)

    def __init__(self, *args, **kws):
        super(MultiChoiceFieldWidget, self).__init__(*args, **kws)
        self.inline = getattr(self.form, 'inline', True)
        self.labelclass = self.inline and "" or "checkbox-inline"
            
    def renderableChoice(self):
        current = self.inputValue()
        base_id = self.htmlId()
        for i, choicet in enumerate(self.choices()):
            yield {'token': choicet.token,
                   'title': choicet.title,
                   'disabled': getattr(choicet, 'disabled', None),
                   'checked': choicet.token in current,
                   'id': base_id + '-' + str(i)}


class SpecialInput(TextareaWidget):
    uvclight.name('SpecialInput')
    adapts(TextField, forms.CreateCourse, IQuizzLayer)
    template = uvclight.get_template('extra_questions.cpt', __file__)

    def update(self):
        super(SpecialInput, self).update()
        efw.need()
        self.questions = None


class EditSpecialInput(TextareaWidget):
    uvclight.name('SpecialInput')
    adapts(TextField, forms.EditCourse, IQuizzLayer)
    template = uvclight.get_template('extra_questions.cpt', __file__)

    def update(self):
        questions = []
        session = self.form.getContentData().content
        extra = session.context.course.extra_questions.strip()
        for qex in extra.split('\n'):
            label, qtype, answers = parse_extra_question_syntax(qex.strip())
            questions.append({
                'question': label,
                'type': qtype,
                'needs_anwer': False,
                'answers': [{'value': a} for a in answers],
            })
        self.questions = json.dumps(questions)
        super(EditSpecialInput, self).update()
        efw.need()
