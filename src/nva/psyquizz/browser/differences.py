# -*- coding: utf-8 -*-

import os
import uvclight
import xlsxwriter
import cStringIO
import shutil
import datetime

from backports import tempfile
from collections import OrderedDict

from cromlech.browser import IRequest, ITraverser
from dolmen.forms.base import FAILURE, SUCCESS
from grokcore.component import MultiAdapter, provides, adapts, name, provider
from nva.psyquizz import hs
from nva.psyquizz.models import IQuizz, IClassSession, ICourse, ICompany
from uvc.design.canvas import IAboveContent
from uvclight.auth import require
from zope.component import getMultiAdapter, queryUtility, getUtilitiesFor
from zope.interface import Interface, classImplements
from zope.location import Location, LocationProxy
from zope.schema import Choice, Set
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from .excel import CHUNK
from .results import CourseStatistics
from ..interfaces import ICompanyRequest
from ..i18n import _


class CompanyCoursesDifference(Location):

    def __init__(self, parent, name, quizz, quizzes):
        self.__parent__ = parent
        self.__name__ = name
        self.quizz = quizz
        self.quizzes = quizzes
        self.all_courses = SimpleVocabulary([
            SimpleTerm(value=c, token=c.id, title=c.name)
            for c in self.__parent__.courses
            if c.quizz_type == quizz.__tablename__
        ])
        self.courses = [c.value for c in self.all_courses]


@provider(IContextSourceBinder)
def courses(context):
    if isinstance(context, CompanyCoursesDifference):
        return context.all_courses
    raise NotImplementedError


class IMultipleCoursesDiff(Interface):

    courses = Set(
        title=_(u"Courses to diff"),
        value_type=Choice(source=courses),
        required=True
    )


class DiffTraverser(MultiAdapter):
    name("diff")
    adapts(ICompany, IRequest)
    provides(ITraverser)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, ns, name):

        def sorter(a, b):
            return cmp(a[0], b[0])

        quizzes = [(n, q) for n, q in getUtilitiesFor(IQuizz)
                   if getattr(q, '__supports_diff__', True)]
        if quizzes:
            quizzes.sort(sorter)
            self.quizzes = OrderedDict(quizzes)

            if not name:
                name, quizz = quizzes[0]
            else:
                quizz = self.quizzes[name]

            return CompanyCoursesDifference(
                self.context, "++diff++" + name, quizz, self.quizzes
            )
        return None


FRONTPAGE = u"""
Auswertungsbericht
„Gemeinsam zu gesunden Arbeitsbedingungen“ – Psychische Belastung erfassen
%s

Befragungen: %s
Auswertung erzeugt: %s
"""


class Export(uvclight.View):
    uvclight.context(CompanyCoursesDifference)
    uvclight.layer(ICompanyRequest)

    def update(self, *courses):
        self.courses = courses

    def render(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "export.xlsx")
            workbook = xlsxwriter.Workbook(filepath)
            nformat = workbook.add_format()
            nformat.set_num_format("0.00")

            fp = FRONTPAGE % (
                self.courses[0].company.name,
                ','.join([x.title for x in self.courses]),
                datetime.datetime.now().strftime('%d.%m.%Y')
            )
            worksheet0 = workbook.add_worksheet('Dokumentation')
            fm = workbook.add_format()
            fm.set_text_wrap()
            worksheet0.set_column(0, 0, 130)
            worksheet0.write(0, 0, fp, fm)

            worksheet = workbook.add_worksheet("Werte")
            global_avg = OrderedDict()
            stats = []
            for course in self.courses:
                stat = CourseStatistics(self.context.quizz, course)
                stat.update({"course": course.id})
                stats.append((course, stat))

            for col, course_stat in enumerate(stats):
                course, stat = course_stat
                worksheet.write(0, col + 2, course.title)
                for row, score in enumerate(stat.statistics["global.averages"]):
                    worksheet.write(row + 1, col + 2, score.average, nformat)
                    avg = global_avg.setdefault(score.title, [])
                    avg.append(score.average)

            worksheet.write(0, 1, 'Durchschnitt')
            for i, x in enumerate(global_avg.items()):
                key, value = x
                worksheet.write(i + 1, 0, key)
                worksheet.write(
                    i + 1, 1, sum(value) / float(len(value)), nformat)

            workbook.close()
            output = cStringIO.StringIO()
            with open(filepath, "rb") as fd:
                shutil.copyfileobj(fd, output)

            output.seek(0)
        return output

        return u"Export"

    def make_response(self, result):
        response = self.responseFactory()
        response.headers[
            "Content-Type"
        ] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        response.headers["Content-Disposition"] = u'attachment; filename="Export.xlsx"'

        def filebody(r):
            data = r.read(CHUNK)
            while data:
                yield data
                data = r.read(CHUNK)

        response.app_iter = filebody(result)
        return response


class CompanyDiff(uvclight.Form):
    name("index")
    require("manage.company")
    uvclight.context(CompanyCoursesDifference)
    uvclight.layer(ICompanyRequest)

    ignoreContent = False
    fields = uvclight.Fields(IMultipleCoursesDiff)
    template = uvclight.get_template("cdiff.cpt", __file__)
    inline = False
    view = None

    @property
    def action_url(self):
        return self.request.path

    @property
    def label(self):
        return _(
            u"Courses difference (${quizz})",
            mapping={"quizz": self.context.quizz.__name__},
        )

    def stats_avg(self):
        stats = []
        global_avg = OrderedDict()
        
        for course in self.context.courses:
            stat = CourseStatistics(self.context.quizz, course)
            stat.update({"course": course.id})
            stats.append(stat)
            for x in stat.statistics["global.averages"]:
                avg = global_avg.setdefault(x.title, [])
                avg.append(x.average)
        avg = []
        for question, scores in global_avg.items():
            avg.append(sum(scores) / float(len(scores)))
        return stats, avg

    def updateActions(self):
        action, result = uvclight.Form.updateActions(self)
        if not action:
            # default
            hs.need()
            self.stats, self.avg = self.stats_avg()
        return action, result

    @uvclight.action(_(u"Difference"))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u"An error occurred."))
            return FAILURE

        hs.need()
        self.context.courses = data['courses']
        self.stats, self.avg = self.stats_avg()
        return SUCCESS

    @uvclight.action(u"Excel Export")
    def handle_export(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u"An error occurred."))
            return FAILURE

        self.view = getMultiAdapter(
            (self.context, self.request), name="export")
        self.view.update(*data["courses"])
        return SUCCESS

    def render(self):
        if self.view is not None:
            return self.view.render()
        return uvclight.Form.render(self)

    def make_response(self, result):
        if self.view is not None:
            return self.view.make_response(result)
        return uvclight.Form.make_response(self, result)


class DiffTabs(uvclight.Viewlet):
    uvclight.viewletmanager(IAboveContent)
    uvclight.order(10)
    uvclight.name("diff-tabs")
    uvclight.layer(ICompanyRequest)
    uvclight.context(CompanyCoursesDifference)

    template = uvclight.get_template("difftabs.cpt", __file__)

    def update(self):
        url = self.view.url(self.context.__parent__)
        self.quizzes = (
            ("%s/++diff++%s" % (url, n), u)
            for n, u in self.context.quizzes.items())
