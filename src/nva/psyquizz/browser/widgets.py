# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from zope.interface import Interface
from grokcore.component import adapts, name
from dolmen.forms.ztk.widgets import choice, date
from uvc.themes.btwidgets.widgets.date import DateFieldWidget
from uvc.themes.btwidgets.widgets.choice import RadioFieldWidget
from dolmen.forms.ztk.widgets.collection import SetField
from dolmen.forms.ztk.widgets.collection import MultiChoiceFieldWidget
from nva.psyquizz.interfaces import IQuizzLayer
from dolmen.forms.ztk.widgets.text import TextareaWidget, TextField
from nva.psyquizz.browser import forms
from nva.psyquizz import efw


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
        #efw.need()
        print "NEEEED"
