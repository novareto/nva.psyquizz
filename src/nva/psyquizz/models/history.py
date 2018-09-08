# -*- coding: utf-8 -*-

from nva.psyquizz import Base
from datetime import datetime
from sqlalchemy import *


class HistoryEntry(Base):

    isEditable = False
    isDeletable = False

    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    action = Column('action', String)
    type = Column('type', String)
    description = Column('description', String)
    date = Column('date', DateTime, default=datetime.utcnow)

    @property
    def traversable_id(self):
        return str(self.id)
