# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

from collections import OrderedDict, namedtuple
from cromlech.sqlalchemy import get_session
from nva.psyquizz.models.criterias import CriteriaAnswer
from sqlalchemy import and_, or_
from sqlalchemy import func
from zope.schema import getFieldsInOrder


Result = namedtuple(
    'Result',
    ('answer', 'id', 'result', 'result_title'))


Average = namedtuple(
    'Average',
    ('title', 'average'))


def average_computation(data):
    for k, v in data.items():
        yield Average(k, float(sum([x.result for x in v]))/len(v))


def sort_data(order, data):

    def sorter(id):
        for k, v in order.items():
            if id in v:
                return k

    ordered = OrderedDict()
    for id, values in data.items():
        title = sorter(id)
        current = ordered.setdefault(title, [])
        current += values

    return ordered


def available_criterias(criterias, session_id):
    available_criterias = {}
    print session_id
    Criteria = namedtuple('Criteria', ('id', 'name', 'amount', 'uid'))
    session = get_session('school')
    all_crits = {x[0]: x[1] for x in session.query(
        CriteriaAnswer.answer, func.count(CriteriaAnswer.answer)).filter(
        CriteriaAnswer.session_id.in_(session_id))
                 .group_by(CriteriaAnswer.answer).all()}

    for crit in criterias:
        for item in crit.items.split('\r\n'):
            total = all_crits.get(item, 0)
            if total >= 1:
                uid = '%s:%s' % (crit.id, item)
                criterias = available_criterias.setdefault(crit.title, [])
                criterias.append(Criteria(crit.id, item, total, uid))

    return available_criterias


def compute(quizz, criterias, averages, filters):

    global_data = OrderedDict()
    users_averages = OrderedDict()

    session = get_session('school')
    answers = session.query(quizz)

    if filters:
        if 'session' in filters:
            answers = answers.filter(
                quizz.session_id == filters['session']
            )

        if 'criterias' in filters:
            # Filter on Criterias
            criterias = (
                and_(quizz.student_id == CriteriaAnswer.student_id,
                     CriteriaAnswer.criteria_id == criteria.id,
                     CriteriaAnswer.answer == criteria.name) for
                criteria in filters['criterias'].values())

            answers = answers.filter(or_(*criterias))

    total = answers.count()
    for answer in answers.all():
        user_data = OrderedDict()  # Per user results
        for field, dd in getFieldsInOrder(quizz.__schema__):

            # We cook the result object.
            field_answer = getattr(answer, field, 0)

            # We set the user response for each question as
            # a list, because we'll use the same method as
            # the global computation for the averages.
            user_data[dd.title] = [Result(
                field,
                dd.title,
                field_answer,
                dd.source.getTerm(field_answer).title
            )]

            # For the global computation
            # We make sure we have the global question set up
            # We'll append all the corresponding answers of all
            # the users
            question = global_data.setdefault(dd.title, [])
            question.append(
                Result(
                    field,
                    dd.title,
                    field_answer,
                    dd.source.getTerm(field_answer).title
                )
            )
        # The computation for a single user is done.
        # We now compute its average.
        sorted_user_answers = sort_data(averages, user_data)
        user_averages = average_computation(sorted_user_answers)
        for av in user_averages:
            group_averages = users_averages.setdefault(av.title, [])
            group_averages.append(av)

    # We do the computation for the global data as well
    sorted_global_answers = sort_data(averages, global_data)
    global_averages = tuple(average_computation(sorted_global_answers))

    return {
        'total': total,
        'users.grouped': users_averages,
        'global.averages': global_averages,
    }


class Scale(object):

    percentage = 0
    number = 0

    def __init__(self, name, weight):
        self.name = name
        self.weight = weight


def groups_scaling(data):

    groups_scaling = OrderedDict()

    for k, av in data.items():
        total = float(len(av))
        scales = (
            Scale('bad', 2.5),
            Scale('mediocre', 3.5),
            Scale('good', 5),
        )

        for a in av:
            for scale in scales:
                if a.average <= scale.weight:
                    scale.number += 1
                    break

        for scale in scales:
            scale.percentage = (scale.number / total) * 100

        groups_scaling[k] = scales

    return groups_scaling
