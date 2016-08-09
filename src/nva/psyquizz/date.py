# -*- coding: utf-8 -*-

from dolmen.clockwork.formatters import DefaultFormDateManager
from dolmen.clockwork.formatters import DefaultFormDatetimeManager


class ASDDataManager(DefaultFormDateManager):
    size = "medium"


class ASDDatetimeManager(DefaultFormDatetimeManager):
    size = "medium"
