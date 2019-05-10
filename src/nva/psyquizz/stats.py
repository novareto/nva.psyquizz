# Copyright (c) 2007-2013 NovaReto GmbH
# cklinger@novareto.de

import json
from copy import deepcopy
from itertools import chain
from collections import OrderedDict, namedtuple
from cromlech.sqlalchemy import get_session
from nva.psyquizz.models.criterias import CriteriaAnswer
from sqlalchemy import and_, or_
from sqlalchemy import func
from zope.schema import getFieldsInOrder


Result = namedtuple(
    'Result',
    ('answer', 'id', 'result', 'result_title', 'description'),
)


Average = namedtuple(
    'Average',
    ('title', 'average'),
)

Sum = namedtuple(
    'Sum',
    ('title', 'total'),
)



def computation(averages, sums, data):
    averages_data = []
    sums_data = []
    for k, v in data.items():
        if k in sums:  # not elif, it could be in both
            sums_data.append(
                Sum(k, sum([x.result for x in v])))
        elif k in averages:
            averages_data.append(
                Average(k, float(sum([x.result for x in v]))/len(v)))
    return averages_data, sums_data


def question_computation(averages, sums, data):
    averages_data = []
    sums_data = []
    for k, v in data.items():
        for at, av in averages.items():
            if k in av:
                averages_data.append(
                    Average(k, float(sum([x.result for x in v]))/len(v)))
        for at, av in sums.items():
            if k in av:
                sums_data.append(
                    Sum(k, sum([x.result for x in v])))
    return averages_data, sums_data


def sort_data(averages, sums, data):

    def sorter(id):
        for k, v in chain(averages.items(), sums.items()):
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
    Criteria = namedtuple('Criteria', ('id', 'name', 'amount', 'uid'))
    session = get_session('school')
    all_crits = {x[0]: x[1] for x in session.query(
        CriteriaAnswer.answer, func.count(CriteriaAnswer.answer)).filter(
        CriteriaAnswer.session_id.in_(session_id))
                 .group_by(CriteriaAnswer.answer).all()}

    for crit in criterias:
        for item in crit.items.split('\r\n'):
            total = all_crits.get(item, 0)
            if total:
                uid = '%s:%s' % (crit.id, item)
                criterias = available_criterias.setdefault(crit.title, [])
                criterias.append(Criteria(crit.id, item, total, uid))

    return available_criterias


def compute(quizz, averages, sums, filters):
    extra_data = OrderedDict()
    global_data = OrderedDict()
    users_averages = OrderedDict()
    users_sums = OrderedDict()

    session = get_session('school')
    answers = session.query(quizz)
    criterias_title = {}
    filtered_criterias = {}
    
    if filters:
        if 'course' in filters:
            answers = answers.filter(
                quizz.course_id == filters['course']
            )
        
        if 'session' in filters:
            answers = answers.filter(
                quizz.session_id == filters['session']
            )
    print answers
    print filters
    print answers.count()
    total = 0
    if 'criterias' in filters:
        criterias = set(
            tuple(v.split(':', 1)) for v in filters['criterias'].keys())
    else:
        criterias = None
    for answer in answers.all():
        user_data = OrderedDict()  # Per user results

        if answer.student:
            student_criterias = set()
            for c in answer.student.criterias:
                criterias_title[str(c.criteria.id)] = c.criteria.title
                student_criterias.add((str(c.criteria.id), c.answer))
                
            if criterias is not None and not student_criterias >= criterias:
                # WE DO NOT MATCH THE CRITERIAS
                continue
            else:
                # WE DO MATCH
                total += 1

            for id, canswer in student_criterias:
                cid = '%s:%s' % (id, criterias_title[id])
                fc = filtered_criterias.setdefault(cid, {})
                fc[canswer] = fc.get(canswer, 0) + 1

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
                dd.source.getTerm(field_answer).title,
                dd.description
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
                    dd.source.getTerm(field_answer).title,
                    dd.description
                )
            )

        extra_questions = getattr(answer, 'extra_questions', None)
        if extra_questions is not None:
            xquestions = json.loads(extra_questions)
            for xk, xv in xquestions.items():
                if not xk in extra_data:
                    extra_data[xk] = {}
                xkres = extra_data[xk]
                if not isinstance(xv, list):
                    xv = [xv]

                for v in xv:
                    if not v in xkres:
                        xkres[v] = 1
                    else:
                        xkres[v] += 1

        # The computation for a single user is done.
        # We now compute its average.
        sorted_user_answers = sort_data(
            averages, sums, user_data)
        user_averages, user_sums = computation(
            averages, sums, sorted_user_answers)

        for av in user_averages:
            group_averages = users_averages.setdefault(av.title, [])
            group_averages.append(av)

        for su in user_sums:
            group_sums = users_sums.setdefault(su.title, [])
            group_sums.append(su)

    # We do the computation for the global data as well
    per_question_averages, per_question_sums = question_computation(
        averages, sums, global_data)
    
    sorted_global_answers = sort_data(
        averages, sums, global_data)

    global_averages, global_sums = computation(
        averages, sums, sorted_global_answers)

    Criteria = namedtuple('Criteria', ('id', 'name', 'amount', 'uid'))
    merged_criterias = {}
    for fid, fc in filtered_criterias.items():
        id, name = fid.split(':', 1)
        for fa, count in fc.items():
            uid = '%s:%s' % (id, fa)
            criterias = merged_criterias.setdefault(name, [])
            criterias.append(Criteria(id, fa, count, uid))

    return {
        'raw': global_data,
        'total': total,
        'users.grouped': users_averages,
        'users.sums': users_sums,
        'global.averages': global_averages,
        'global.sums': global_sums,
        'criterias': merged_criterias,
        'extra_data': extra_data,
        'has_criterias_filter': bool(criterias is None),
        'per_question_averages': per_question_averages,
        'per_question_sums': per_question_sums,
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
