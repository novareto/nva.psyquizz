# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2013 NovaReto GmbH
# # cklinger@novareto.de

import os
import uvclight
import xlsxwriter
import cStringIO
import shutil

from backports import tempfile
from uvclight.auth import require
from nva.psyquizz.models import IQuizz
from cromlech.sqlalchemy import get_session
from zope import interface, component
from zope.schema import getFieldsInOrder

from . import CHUNK


def calculator():
    session = get_session('school')
    def calculate_results(quizz):
        return session.query(quizz).all()
    return calculate_results


class StatuslisteExport(uvclight.View):
    uvclight.context(interface.Interface)
    require('manage.company')

    def render(self):
        computer = calculator()
        r = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "export.xlsx")
            workbook = xlsxwriter.Workbook(filepath)

            for name, quizz in component.getUtilitiesFor(IQuizz):
                quizz_results = computer(quizz)
                worksheet = workbook.add_worksheet(name)
                worksheet.write(0, 0, 'Session id')
                for row, answer in enumerate(quizz_results):
                    worksheet.write(row + 1, 0, str(answer.session_id))
                    for col, f in enumerate(getFieldsInOrder(quizz.__schema__)):
                        field_name, field = f
                        result = getattr(answer, field_name, 'NA')
                        title = '%s [%s]' % (
                            field_name, field.vocabulary.__name__)
                        worksheet.write(0, col + 1, title)
                        worksheet.write(row + 1, col + 1, result)

            workbook.close()
            output = cStringIO.StringIO()
            with open(filepath, "rb") as fd:
                shutil.copyfileobj(fd, output)

            output.seek(0)
 
        return output

    def make_response(self, result):
        response = self.responseFactory()
        response.headers[
            "Content-Type"
        ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response.headers["Content-Disposition"] = (
            u'attachment; filename="Export.xlsx"')

        def filebody(r):
            data = r.read(CHUNK)
            while data:
                yield data
                data = r.read(CHUNK)

        response.app_iter = filebody(result)
        return response
