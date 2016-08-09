# -*- coding: utf-8 -*-

SESSION_NAME = ''


import uvclight
from cromlech.browser import IPublicationRoot
from cromlech.sqlalchemy import get_session
from sqlalchemy import String, Integer, Column
from sqlalchemy.ext.declarative import declarative_base
from uvclight.backends.sql import SQLPublication
from ul.auth import SecurePublication
from ul.browser.decorators import with_zcml, with_i18n
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.interface import implementer
from zope.location import Location, ILocation
from dolmen.sqlcontainer import SQLContainer
from fanstatic import Library, Resource, Group
from siguvtheme.resources import bootstrap_css, siguv_css


library = Library('nva.psyquizz', 'static')

lbjs = Resource(library, 'ekko-lightbox.min.js')
lbcss = Resource(library, 'ekko-lightbox.min.css')

lbg = Group([lbjs, lbcss])

#chartjs = Resource(library, 'Chart.js')
#charthbar = Resource(library, 'Chart.StackedBar.js', depends=[chartjs])

charthjs = Resource(library, 'ChartNew.js')
quizzcss = Resource(library, 'quizz.css')
quizzjs = Resource(library, 'quizz.js', depends=[charthjs, ])
clipboard_js = Resource(library, 'clipboard.min.js')
wysiwyg_js = Resource(library, 'summernote.min.js', bottom=True)
font_css = Resource(library, 'font-awesome.min.css')
wysiwyg_css = Resource(library, 'summernote.css',
                       depends=[bootstrap_css, siguv_css, font_css])
editor = Resource(library, 'quizzeditor.js', depends=[wysiwyg_js], bottom=True)
wysiwyg = Group([wysiwyg_js, wysiwyg_css, editor])

Base = declarative_base()
