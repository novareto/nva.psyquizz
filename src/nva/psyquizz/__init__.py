# -*- coding: utf-8 -*-

# Monkey patching
from zope.interface import verify
from dolmen.menu import meta


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
from siguvtheme.resources import datepicker_de, bootstrap_css, siguv_css


library = Library('nva.psyquizz', 'static')

lbjs = Resource(library, 'ekko-lightbox.min.js')
lbcss = Resource(library, 'ekko-lightbox.min.css')

lbg = Group([lbjs, lbcss])

quizzcss = Resource(library, 'quizz.css')
quizzjs = Resource(library, 'quizz.js')
clipboard_js = Resource(library, 'clipboard.min.js')
wysiwyg_js = Resource(library, 'summernote.min.js', bottom=True)
font_css = Resource(library, 'font-awesome.min.css')
wysiwyg_css = Resource(library, 'summernote.css', depends=[font_css])
editor = Resource(library, 'quizzeditor.js', depends=[wysiwyg_js], bottom=True)
wysiwyg = Group([wysiwyg_js, wysiwyg_css, editor])
hsb = Resource(library, 'highcharts.js')
hsb_export = Resource(library, 'exporting.js', depends=[hsb])
hs = Resource(library, 'highcharts-more.js', depends=[hsb, hsb_export])

startendpicker = Resource(library, 'picker.js', depends=[datepicker_de])


# ExtraFieldsWidget
efw_manifest = Resource(library, 'efw/manifest.js', bottom=True)
efw_vendor = Resource(library, 'efw/vendor.js', depends=[efw_manifest,], bottom=True)
efw_app = Resource(library, 'efw/app.js', depends=[efw_vendor,], bottom=True)


efw = Group([efw_vendor, efw_app, efw_manifest])



Base = declarative_base()
