# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from . import IntIds
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from uvclight.directives import traversable
from zope.interface import Interface, implementer
from zope.location import Location
from .interfaces import IAccount


@implementer(IAccount)
class Account(Base, Location):
    
    __tablename__ = 'accounts'

    email = Column('email', String, primary_key=True)
    name = Column('name', String)
    password = Column('password', String)
    activation = Column('activation', String)
    activated = Column('activated', DateTime)

    _companies = relationship(
        "Company", backref=backref("account", uselist=False),
        collection_class=IntIds)

    @property
    def id(self):
        return self.email

    @property
    def __name__(self):
        return self.email

    @__name__.setter
    def __name__(self, value):
        pass
    
    def __getitem__(self, key):
        try:
            company = self._companies[int(key)]
            return self.locate(company)
        except (KeyError, ValueError):
            return None

    def locate(self, company):
        company.__parent__ = self
        return company

    def __iter__(self):
        return (self.locate(i) for i in self._companies)
    
