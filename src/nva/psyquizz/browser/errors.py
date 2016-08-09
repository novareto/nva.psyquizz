# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de


import logging
from ul.browser.errors import PageError500, PageError404


log = logging.getLogger('UVCPsyquizz')


class PageError500(PageError500):
    def render(self):
        log.exception(self.context)
        return u"Es ist ein Fehler aufgetreten"


class PageError404(PageError404):
    def render(self):
        log.exception(self.context)
        return u"Diese Seite kann nicht gefunden werden."
