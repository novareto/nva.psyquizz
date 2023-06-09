# -*- coding: utf-8 -*-

import os
import uvclight
import xlsxwriter
import cStringIO
import shutil
import datetime

from backports import tempfile
from collections import OrderedDict, Counter, defaultdict
from sqlalchemy import func, and_

from cromlech.browser import IRequest, ITraverser
from cromlech.sqlalchemy import get_session
from dolmen.forms.base import FAILURE, SUCCESS
from grokcore.component import MultiAdapter, provides, adapts, name, provider
from nva.psyquizz import hs, hsb_bullet
from nva.psyquizz.models import IQuizz, ICourse, ICompany
from uvc.design.canvas import IAboveContent
from uvclight.auth import require
from zope.component import getMultiAdapter, queryUtility, getUtilitiesFor
from zope.interface import Interface
from zope.location import Location
from zope.schema import Choice, Set
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from .excel import CHUNK
from .results import CourseStatistics, SessionStatistics, get_filters
from ..interfaces import ICompanyRequest
from ..i18n import _
from ..models import Course, Student, ClassSession
from nva.psyquizz.models.deferred import check_quizz


def have_courses_to_compare(context, threshold=7):
    if ICompany.providedBy(context):
        types = Counter()
        session = get_session('school')
        courses = session.query(Course.quizz_type).\
                  filter(Course.company_id == context.id).\
                  join(Student, and_(
                      Student.course_id==Course.id,
                      Student.completion_date != None
                  )).\
                  group_by(Course.id).\
                  having(func.count(Student.access) >= threshold)
        for (quizz_type,) in courses.all():
            if types[quizz_type] == 1:
                return True
            types[quizz_type] += 1
        return False

    raise NotImplementedError


@provider(IContextSourceBinder)
def sessions(context, threshold=7):
    if ICourse.providedBy(context):
        session = get_session('school')
        sessions = session.query(ClassSession).\
                  filter(Course.id == context.id).\
                  filter(ClassSession.course_id == context.id).\
                  join(Student, and_(
                      Student.session_id==ClassSession.id,
                      Student.completion_date != None
                  )).\
                  group_by(ClassSession.id).\
                  having(func.count(Student.access) >= threshold)
        return SimpleVocabulary([
            SimpleTerm(value=s, token=s.id, title=s.title)
            for s in sessions
        ])
    raise NotImplementedError


class CompanyCoursesDifference(Location):
    criterias = None

    def __init__(self, parent, name, quizz, quizzes):
        self.__parent__ = parent
        self.__name__ = name
        self.quizz = quizz
        self.quizzes = quizzes

        session = get_session('school')
        courses = session.query(Course).\
                  filter(Course.quizz_type == quizz.__tablename__).\
                  filter(Course.company_id == parent.id).\
                  join(Student, and_(
                      Student.course_id==Course.id,
                      Student.completion_date != None
                  )).\
                  group_by(Course.id).\
                  having(func.count(Student.access) >= 7)

        rc = []
        for c in courses.all():
            title = c.name
            if len(list(c.sessions)) > 1:
                title = "%s [Durchschnitt]" %(c.name)
            rc.append(SimpleTerm(value=c, token=c.id, title=title))

#        self.all_courses = SimpleVocabulary([
#            SimpleTerm(value=c, token=c.id, title=c.name)
#            for c in courses.all()
#        ])
        self.all_courses = SimpleVocabulary(rc)
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

class IMultipleSessionsDiff(Interface):

    sessions = Set(
        title=_(u"Sessions to diff"),
        value_type=Choice(source=sessions),
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
            for name, quizz in quizzes:
                if check_quizz(name, quizz, self.context):
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
            #    worksheet.write(
            #        i + 1, 1, sum(value) / float(len(value)), nformat)

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



class SessionsExport(Export):
    uvclight.name('export')
    uvclight.context(ICourse)
    uvclight.layer(ICompanyRequest)

    def update(self, *sessions):
        self.sessions = sessions
        self.quizz = queryUtility(IQuizz, name=self.context.quizz_type)

    def render(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "export.xlsx")
            workbook = xlsxwriter.Workbook(filepath)
            nformat = workbook.add_format()
            nformat.set_num_format("0.00")

            filters = get_filters(self.request)
            filters["course"] = self.context.id

            fp = FRONTPAGE % (
                self.sessions[0].course.company.name,
                ','.join([x.title for x in self.sessions]),
                datetime.datetime.now().strftime('%d.%m.%Y')
            )

            if 'criterias' in filters:
                fp += '\nDiese Auswertung basiert auf folgenden Kriterien: %s' % (
                    ', '.join((c.name for c in filters['criterias'].values())))



            worksheet0 = workbook.add_worksheet('Dokumentation')
            fm = workbook.add_format()
            fm.set_text_wrap()
            worksheet0.set_column(0, 0, 130)
            worksheet0.write(0, 0, fp, fm)

            worksheet = workbook.add_worksheet("Werte")
            global_avg = OrderedDict()
            stats = []

            for session in self.sessions:
                stat = SessionStatistics(self.quizz, session)
                stat.update(filters)
                stats.append((session, stat))

            for col, session_stat in enumerate(stats):
                course, stat = session_stat
                worksheet.write(0, col + 1, course.title)
                for row, score in enumerate(stat.statistics["global.averages"]):
                    worksheet.write(row + 1, col + 1, score.average, nformat)
                    avg = global_avg.setdefault(score.title, [])
                    avg.append(score.average)

            #worksheet.write(0, 1, 'Durchschnitt')
            for i, x in enumerate(global_avg.items()):
                key, value = x
                worksheet.write(i + 1, 0, key)
            #    worksheet.write(
            #        i + 1, 1, sum(value) / float(len(value)), nformat)

            workbook.close()
            output = cStringIO.StringIO()
            with open(filepath, "rb") as fd:
                shutil.copyfileobj(fd, output)

            output.seek(0)
        return output

        return u"Export"


class SessionsDiff(uvclight.Form):
    name("sessions.diff")
    require("manage.company")
    uvclight.context(ICourse)
    uvclight.layer(ICompanyRequest)

    ignoreContent = False
    fields = uvclight.Fields(IMultipleSessionsDiff)
    inline = False
    view = None
    _colors = None
    rainbow = (
        '#000000',
        '#0000ff',
        '#00ffff',
        '#ff00a2',
        '#6f00a2',
        '#6fffa2'
    )

    @property
    def quizz(self):
        return queryUtility(IQuizz, name=self.context.quizz_type)

    @property
    def template(self):
        if self.context.quizz_type == 'quizz5':
            hsb_bullet.need()
            return uvclight.get_template("quizz5_session_diff.pt", __file__)
        return uvclight.get_template("cdiff.cpt", __file__)

    @property
    def colors(self):
        if self._colors is None:
            if self.context.quizz_type != 'quizz5':
                raise NotImplementedError(
                    'No colors for quizz ' + self.context.quizz_type)
            self._colors = self.quizz().get_boundaries()
        return self._colors

    @property
    def action_url(self):
        return self.request.path

    @property
    def label(self):
        return _(
            u"Sessions difference (${course})",
            mapping={"course": self.context.title},
        )

    def stat_title(self, stat):
        return stat.session.title

    def stats_avg(self, sessions):
        stats = []
        global_avg = OrderedDict()
        criterias = defaultdict(dict)
        filters = get_filters(self.request)
        filters["course"] = self.context.id

        seen = set()
        for session in sessions:
            stat = SessionStatistics(self.quizz, session)
            stat.update(filters)
            for title, cc in stat.statistics['criterias'].items():
                for c in cc:
                    if c.uid not in seen:
                        if c.amount >= 7:
                            criterias[title][c.uid] = {
                                'name': c.name,
                                'selected': c.uid in filters.get(
                                    'criterias', {})
                            }
                        seen.add(c.uid)
                    elif c.amount < 7 and c.uid in criterias[title]:
                        del criterias[title][c.uid]


            stats.append(stat)
            for x in stat.statistics["global.averages"]:
                avg = global_avg.setdefault(x.title, [])
                avg.append(x.average)

        avg = []
        for question, scores in global_avg.items():
            avg.append(sum(scores) / float(len(scores)))

        return stats, avg, criterias

    def updateActions(self):
        action, result = uvclight.Form.updateActions(self)
        if not action:
            # default
            hs.need()
            self.stats, self.avg, self.criterias = self.stats_avg([])
        return action, result

    @uvclight.action(_(u"Difference"))
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u"An error occurred."))
            return FAILURE

        hs.need()
        self.stats, self.avg, self.criterias = self.stats_avg(data['sessions'])
        return SUCCESS

    @uvclight.action(u"Export")
    def handle_export(self):
        data, errors = self.extractData()
        if errors:
            self.flash(_(u"An error occurred."))
            return FAILURE
        self.view = getMultiAdapter(
            (self.context, self.request), name="export")
        self.view.update(*data["sessions"])
        return SUCCESS

    def render(self):
        if self.view is not None:
            return self.view.render()
        return uvclight.Form.render(self)

    def make_response(self, result):
        if self.view is not None:
            return self.view.make_response(result)
        return uvclight.Form.make_response(self, result)


class CompanyDiff(uvclight.Form):
    name("index")
    require("manage.company")
    uvclight.context(CompanyCoursesDifference)
    uvclight.layer(ICompanyRequest)

    criterias = None
    ignoreContent = False
    fields = uvclight.Fields(IMultipleCoursesDiff)
    template = uvclight.get_template("cdiff.cpt", __file__)
    inline = False
    view = None

    def stat_title(self, stat):
        return stat.course.title

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
            print course.id
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
