# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import json
import uvclight

from collections import OrderedDict, namedtuple
from cromlech.browser import IView
from grokcore.component import name
from nva.psyquizz import hs, hsb_bullet
from nva.psyquizz.models import IQuizz, IClassSession, ICourse
from nva.psyquizz.models.quizz.quizz2 import IQuizz2
from nva.psyquizz.models.quizz.quizz1 import Quizz1
from nva.psyquizz.models.quizz.quizz3 import IQuizz3
from nva.psyquizz.models.quizz.quizz5 import IQuizz5
from uvclight.auth import require
from zope.component import getUtility, getMultiAdapter
from zope.schema import getFieldsInOrder
from zope.location import LocationProxy

from ..interfaces import ICompanyRequest
from ..stats import compute, groups_scaling
from ..extra_questions import parse_extra_question_syntax


def get_filters(request):

    def extract_criteria(str):
        cid, name = str.split(':', 1)
        return str, int(cid), name

    filters = {}
    Criteria = namedtuple('Criteria', ('id', 'name'))

    criterias = [item for name, item in request.form.items()
                 if name.startswith('criteria-') and item != 'reset']

    filters['criterias'] = {
        uid: Criteria(cid, name) for uid, cid, name in
        map(extract_criteria, criterias)}
    return filters


class CourseStatistics(object):

    def __init__(self, quizz, course):
        self.quizz = quizz
        self.averages = quizz.__schema__.queryTaggedValue('averages') or {}
        self.sums = quizz.__schema__.queryTaggedValue('sums') or {}
        self.course = course

    def update(self, filters):
        self.filters = filters
        self.statistics = compute(
            self.quizz, self.averages, self.sums, self.filters)
        if 'criterias' in filters:
            for criteria in filters['criterias']:
                for title, cc in self.statistics['criterias'].items():
                    for c in cc:
                        if criteria == c.uid and c.amount < 7:
                            raise NotImplementedError()

        self.users_statistics = groups_scaling(
            self.statistics['users.grouped'])
        self.xAxis = [
        x.encode('iso-8859-1') for x in self.users_statistics.keys() if x]
        bad = dict(name="viel / zutreffend", data=[], color="#62B645")
        mid = dict(name="mittelmäßig", data=[], color="#FFCC00")
        good = dict(name="wenig / nicht zutreffend", data=[], color="#D8262B")
        for x in self.users_statistics.values():
            good['data'].append(float("%.2f" % x[0].percentage))
            mid['data'].append(float("%.2f" % x[1].percentage))
            bad['data'].append(float("%.2f" % x[2].percentage))
        self.series = json.dumps([good, mid, bad])
        self.rd1 = [x.average for x in self.statistics['global.averages']]
        self.rd = [float("%.2f" % x.average)
                   for x in self.statistics['global.averages']]

        criterias = []
        for crits in self.statistics['criterias'].values():
            for crit in crits:
                criterias.append([crit.name, crit.amount])
        self.json_criterias = json.dumps(criterias)

        self.extra_questions_order = OrderedDict()
        for iface in self.quizz.additional_extra_fields(self.course):
            for _, field in getFieldsInOrder(iface):
                 self.extra_questions_order[field.description] = [
                     t.title for t in field.vocabulary
                 ]

        if self.course.extra_questions:
            questions = self.course.extra_questions.strip().split('\n')
            for question in questions:
                label, qtype, values = parse_extra_question_syntax(question)
                if not label in self.extra_questions_order:
                    self.extra_questions_order[label] = values

                if not label in self.statistics['extra_data']:
                    self.statistics['extra_data'][label] = {}
                extra_answers = self.statistics['extra_data'][label]
                for value in values:
                    if not value in extra_answers:
                        extra_answers[value] = 0


class SessionStatistics(CourseStatistics):

    def __init__(self, quizz, session):
        self.quizz = quizz
        self.course = session.course
        self.session = session
        self.averages = quizz.__schema__.queryTaggedValue('averages') or {}
        self.sums = quizz.__schema__.queryTaggedValue('sums') or {}

    def update(self, filters):
        filters['session'] = self.session.id
        CourseStatistics.update(self, filters)


class Quizz2Charts(uvclight.View):
    require('manage.company')
    name('charts')
    uvclight.context(IQuizz2)

    template = uvclight.get_template('chart_results.pt', __file__)
    general_stats = None

    def jsonify(self, da):
        return json.dumps(da)

    def update(self, stats, general_stats=None):
        hs.need()
        self.stats = stats
        self.general_stats = general_stats


class Quizz5Charts(Quizz2Charts):
    uvclight.context(IQuizz5)
    template = uvclight.get_template('quizz5_result.pt', __file__)
    description = u"""
        <p>
	  Im Folgenden werden die Befragungsergebnisse dargestellt und wie sich diese auf die
	  Gesundheit der Mitarbeiterinnen und Mitarbeiter auswirken. Der blaue Strich kennzeichnet dabei
	  das Ergebnis für den jeweiligen Bereich. Ergebnisse innerhalb des roten Balkens deuten auf ein
	  erhöhtes Gesundheitsrisiko hin, Ergebnisse innerhalb des gelben Balkens stehen für ein leicht
	  erhöhtes Gesundheitsrisiko und bei Ergebnissen innerhalb des grünen Balkens scheint alles in
	  Ordnung.
        </p>
        <p>
	  Die Wirkung der einzelnen Bereiche aus der Befragung auf die Gesundheit ist unterschiedlich
	  stark, was sich in der Länge der farblichen Balken widerspiegelt. Es gibt zwei Bereiche mit einem
	  insgesamt geringeren Risiko (Vollständigkeit der Aufgabe, Variabilität) hier wird kein roter Balken
	  dargestellt. Auf der anderen Seite gibt es Bereiche mit einem erhöhten Risiko (z.B. Soziale
	  Drucksituationen) hier ist der rote Balken besonders lang.
        </p>
        <p>
	  Außerdem gibt es Bereiche, sogenannte Ressourcen, bei denen gilt „je mehr desto besser“.
	  Deshalb beginnt beispielsweise bei „Handlungsspielraum“ die Grafik mit dem roten Balken und
	  endet mit dem grünen.
        </p>
        <p>
	    Eine Definition der einzelnen Bereiche (z. B. Vollständigkeit der Aufgabe) erhalten Sie, indem Sie mit
	    der Mouse über den Text der Bereiche fahren. Eine Gesamtübersicht der Bereichsdefinitionen können Sie
	    <a target="_blank" href="/fanstatic/nva.psyquizz/kurzerlauterungen_fbgu_skalen.pdf">hier</a> herunterladen.
        </p>

    """

    def update(self, stats, general_stats=None):
        hsb_bullet.need()
        self.colors = self.context.get_boundaries()
        super(Quizz5Charts, self).update(stats, general_stats)

        current = self.stats.filters.get('criterias', {})
        criterias = self.stats.statistics['criterias']



class Quizz3Charts(Quizz2Charts):
    uvclight.context(IQuizz3)
    template = uvclight.get_template('quizz3_result.pt', __file__)

    def percent(self, nb):
        return (float(nb) / self.nb_answer) * 100

    def update(self, stats, general_stats=None):
        super(Quizz3Charts, self).update(stats, general_stats = None)
        self.stats = stats
        self.general_stats = general_stats

        self.board = OrderedDict((
            (u"schlecht", 0),
            (u"mittelmäßig", 0),
            (u"gut", 0),
            (u"sehr gut", 0),
        ))

        self.ausp = {
                u"schlecht":"5 bis 20",
                u"mittelmäßig":"21 bis 27",
                u"gut":"28 bis 32",
                u"sehr gut":"33 bis 36",
                }

        results_count = {}
        users_results = {}
        sums = self.stats.statistics['users.sums']
        self.nb_answer = len(sums.values()[0])

        for id, answers in sums.iteritems():
            for idx, answer in enumerate(answers):
                if idx not in users_results:
                    users_results[idx] = 0
                if id in summing_methods:
                    total = summing_methods[id](answer.total)
                else:
                    total = answer.total

                users_results[idx] += total
        summe = 0
        for result in users_results.values():
            if result < 21:
                self.board[u"schlecht"] += 1
            elif result < 28:
                self.board[u"mittelmäßig"] += 1
            elif result < 33:
                self.board[u"gut"] += 1
            else:
                self.board[u"sehr gut"] += 1
            summe += result
            if result not in results_count:
                results_count[result] = 0
            results_count[result] += 1
        self.results_count = results_count
        self.users_results = users_results
        self.av = float(summe) / len(users_results)


def psychische_leistungsreserven(total):
    if total < 4:
        return 1
    if total < 7:
        return 2
    if total < 10:
        return 3
    return 4


summing_methods = {
    u'Psychische Leistungsreserven': psychische_leistungsreserven,
}


class Quizz1Charts(uvclight.View):
    require('manage.company')
    name('charts')
    uvclight.context(Quizz1)

    template = uvclight.get_template('quizz_results.pt', __file__)

    def extra_title(self):
        title = u"Zusatzfragen "
        if self.context.__parent__.course.extra_questions:
            title += " - eigene Zusatzfragen"
        if self.context.__parent__.course.fixed_extra_questions:
            title += " - vordefinierte Zusatzfragen"
        return title

    def jsonify(self, da):
        return json.dumps(da)

    def update(self, stats, general_stats=None):
        hs.need()
        self.stats = stats
        self.general_stats = general_stats

        good = dict(name="Eher Ja", data=[], color="#62B645")
        bad = dict(name="Eher Nein", data=[], color="#D8262B")

        self.descriptions = json.dumps(
            self.context.__schema__.getTaggedValue('descriptions'))

        self.xAxis_labels = {
            k.title: k.description for id, k in
            getFieldsInOrder(self.context.__schema__)}

        xAxis = []
        for key, answers in self.stats.statistics['raw'].items():
            xAxis.append(key)
            yesses = 0
            noes = 0
            total = 0
            for answer in answers:
                total += 1
                if answer.result is True:
                    yesses += 1
                else:
                    noes +=1

            good['data'].append(float(yesses)/total * 100)
            bad['data'].append(float(noes)/total * 100)

        self.xAxis = json.dumps(xAxis)
        self.series = json.dumps([good, bad])


class SessionResults(uvclight.Page):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        quizz = getUtility(IQuizz, self.context.course.quizz_type)
        filters = get_filters(self.request)
        stats = SessionStatistics(quizz, self.context)
        stats.update(filters)

        if 'criterias' in filters:
            general_stats = SessionStatistics(quizz, self.context)
            general_stats.update({})

            for criteria in filters['criterias']:
                for title, cc in general_stats.statistics['criterias'].items():
                    for c in cc:
                        if criteria == c.uid and c.amount < 7:
                            raise NotImplementedError()

        else:
            general_stats = None

        quizz_obj = LocationProxy(quizz(), container=self.context, name='')
        self.charts = getMultiAdapter(
            (quizz_obj, self.request), IView, name="charts")
        self.charts.update(stats, general_stats)

    def render(self):
        result = self.charts.render()
        return result


class CourseResults(uvclight.Page):
    require('manage.company')
    uvclight.context(ICourse)
    uvclight.layer(ICompanyRequest)

    template = uvclight.get_template('chart_results.pt', __file__)
    general_stats = None

    def jsonify(self, da):
        return json.dumps(da)

    def update(self):
        hs.need()
        quizz = getUtility(IQuizz, self.context.quizz_type)
        stats = CourseStatistics(quizz, self.context)
        filters = get_filters(self.request)
        filters['course'] = self.context.id
        stats.update(filters)

        if 'criterias' in filters:
            general_stats = CourseStatistics(quizz, self.context)
            general_stats.update({'course': self.context.id})

            for criteria in filters['criterias']:
                for title, cc in general_stats.statistics['criterias'].items():
                     for c in cc:
                         if criteria == c.uid and c.amount < 7:
                             raise NotImplementedError()
#                for title, cc in general_stats.statistics['criterias'].items():
#                    for c in cc:
#                        if criteria == c.uid and c.amount < 7:
#                            raise NotImplementedError()

        else:
            general_stats = None

        quizz_obj = LocationProxy(quizz(), container=self.context, name='')
        self.charts = getMultiAdapter(
            (quizz_obj, self.request), IView, name="charts")
        self.charts.update(stats, general_stats)

    def render(self):
        return self.charts.render()


class Export(uvclight.View):
    require('manage.company')
    uvclight.context(IClassSession)
    uvclight.layer(ICompanyRequest)

    def update(self):
        action = self.request.form.get('action', None)
        assert action is not None
        if action == 'PDF' or action == "wai" or action== 'kfza':
            self.view = getMultiAdapter(
                (self.context, self.request), name="pdf")
            self.view.update()
        elif action == 'Excel':
            self.view = getMultiAdapter(
                (self.context, self.request), name="excel")
            self.view.update()
        else:
            raise NotImplementedError('Action unknown')

    def render(self):
        return self.view.render()

    def make_response(self, result):
        return self.view.make_response(result)
