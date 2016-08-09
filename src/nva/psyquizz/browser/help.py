# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight

from zope.interface import Interface
from uvc.design.canvas import IAboveContent
from .forms import CreateCourse, CreateCompany, CreateCriterias, EditCriteria
from .forms import CourseStats
from .ckhp import AccountHomepage, ExampleText


class HelpPage(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IAboveContent)
    uvclight.baseclass()
    template = uvclight.get_template('helppage.cpt', __file__)


class HelpCompany(HelpPage):
    uvclight.view(AccountHomepage)
    template = uvclight.get_template('helpfrontpage.cpt', __file__)


class HelpFrontPage(HelpPage):
    uvclight.view(CreateCompany)
    template = uvclight.get_template('helpcompany.cpt', __file__)


class HelpAddCriteria(HelpPage):
    uvclight.view(CreateCriterias)
    template = uvclight.get_template('helpcriterias.cpt', __file__)


class HelpEditCriteria(HelpAddCriteria):
    uvclight.view(EditCriteria)


class HelpCourse(HelpPage):
    uvclight.view(CreateCourse)
    template = uvclight.get_template('helpcourse.cpt', __file__)


class HelpLetter(HelpPage):
    uvclight.view(ExampleText)
    template = uvclight.get_template('helpletter.cpt', __file__)
