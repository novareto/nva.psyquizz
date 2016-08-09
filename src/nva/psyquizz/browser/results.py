# -*- coding: utf-8 -*-

import json
from cromlech.sqlalchemy import get_session
from zope.component import getUtility
from ..models import IQuizz, Student, CriteriaAnswer

class Results(object):

    colors = {
        1: 'rgba(212, 15, 20, 0.9)',
        2: 'rgba(212, 15, 20, 0.9)',
        3: 'rgba(255, 204, 0, 0.9)',
        4: 'rgba(81, 174, 49, 0.9)',
        5: 'rgba(81, 174, 49, 0.9)',
        }

    labels = {
        1: '+',
        3: '+ / -',
        5: '-',
        }
   
    def jsonify(self, da):
        return json.dumps(da)

    def avg(self, res):
        return (
            (1.0 * res[1]) / 100.0 +
            (2.0 * res[2]) / 100.0 +
            (3.0 * res[3]) / 100.0 +
            (4.0 * res[4]) / 100.0 +
            (5.0 * res[5]) / 100.0)
        
    def students_ids(self, session):
        criterias = self.criterias
        if not criterias:
            return None

        students_ids = None
        for criteria_id, values in criterias.items():
            if values:
                query = session.query(CriteriaAnswer.student_id).filter(
                    CriteriaAnswer.criteria_id == criteria_id).filter(
                        CriteriaAnswer.answer.in_(list(values)))
                if students_ids is None:
                    students_ids = set([q[0] for q in query.all()])
                else:
                    students_ids &= set([q[0] for q in query.all()])

        return students_ids

    def count_students(self, session, qtype, cid=None, sid=None, restrict=None):
        students = session.query(Student).filter(Student.quizz_type == qtype)
        if cid is not None:
            students = students.filter(Student.course_id == cid)
        if sid is not None:
            students = students.filter(Student.session_id == sid)
        if restrict:
            students = students.filter(Student.access.in_(restrict))

        return students.count()

    def get_data(self, qtype, cid=None, sid=None, extra_questions=None):
        session = get_session('school')
        quizz = getUtility(IQuizz, name=qtype)
        stats = quizz.__stats__
        data = {}

        restrict = self.students_ids(session)
        if restrict is not None and not restrict:
            nb_students = 0
        else:
            nb_students = self.count_students(session, qtype, cid, sid, restrict)
            if nb_students:
                answers = session.query(quizz)
                if sid is not None:
                    answers = answers.filter(quizz.session_id == sid)
                if cid is not None:
                    answers = answers.filter(quizz.course_id == cid)

                if restrict is not None:
                    answers = answers.filter(quizz.student_id.in_(restrict))

                answers = list(answers)
                if answers:
                    data[self.context.quizz_type] = stats(
                        nb_students, answers, extra_questions, quizz)
        return data
