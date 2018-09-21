# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2013 NovaReto GmbH
# # cklinger@novareto.de


import uvclight

from uvclight.auth import require
from nva.psyquizz.models import IQuizz
from cromlech.sqlalchemy import get_session
from zope import interface, component, schema


class StatuslisteExport(uvclight.View):
    uvclight.context(interface.Interface)
    require('manage.company')

    def calculateResults(self):
        rc = {}
        session = get_session('school')
        for name, quizz in component.getUtilitiesFor(IQuizz):
            rc[name] = session.query(quizz).all()
        return rc

    def render(self):
        results = self.calculateResults()
        r = {}
        for name, quizz in component.getUtilitiesFor(IQuizz):
            rows = [[]]
            start = True
            quizz_results = results[name]
            for field_name, field in schema.getFieldsInOrder(quizz.__schema__):
                import pdb; pdb.set_trace() 
                rows[0].append(field_name)
                res = []
                for result in quizz_results:
                    res.append(getattr(result, field_name, 'NA'))
                rows.append(res)
            r[name] = rows

        import pdb; pdb.set_trace() 
        return results
