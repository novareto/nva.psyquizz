# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import uvclight
from os import path
from dolmen.template import TALTemplate
from zope.interface import Interface
from uvc.design.canvas import IAboveContent
from .forms import CreateCourse, CreateCompany, CreateCriterias, EditCriteria
from .invitations import ExampleText



PATH = path.dirname(__file__)

class HelpPage(uvclight.Viewlet):
    uvclight.context(Interface)
    uvclight.viewletmanager(IAboveContent)
    uvclight.baseclass()
    template = TALTemplate(PATH+'/help-templates/helppage.cpt')


#class HelpCompany(HelpPage):
#    uvclight.view(AccountHomepage)
#    template = uvclight.get_template('helpfrontpage.cpt', __file__)


class HelpFrontPage(HelpPage):
    uvclight.view(CreateCompany)
    template = TALTemplate(PATH +'/help-templates/helpcompany.cpt')


class HelpAddCriteria(HelpPage):
    uvclight.view(CreateCriterias)
    template = TALTemplate(PATH+'/help-templates/helpcriterias.cpt')


class HelpEditCriteria(HelpAddCriteria):
    uvclight.view(EditCriteria)


class HelpCourse(HelpPage):
    uvclight.view(CreateCourse)
    template = TALTemplate(PATH + './help-templates/helpcourse.cpt')


class HelpLetter(HelpPage):
    uvclight.view(ExampleText)
    template = TALTemplate(PATH + './help-templates/helpletter.cpt')
