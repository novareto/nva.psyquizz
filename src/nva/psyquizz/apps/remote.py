# -*- coding: utf-8 -*-

import json
from cromlech.sqlalchemy import SQLAlchemySession
from ..models import Student
from cromlech.webob import Response


class Application(object):

    def __init__(self, session_key, engine, name):
        self.engine = engine

    def get(self, obj):
        return {
            'success': True,
            'quizz_type': obj.course.quizz_type,
            }

    def post(self, obj):
        return {
            'success': True,
        }

    def __call__(self, environ, start_response):
        id = environ['PATH_INFO'][1:]
        method = getattr(self, environ.get('REQUEST_METHOD', 'GET').lower())

        def make_response(result):
            json_result = json.dumps(result)
            response = Response()
            response.write(json_result)
            response.headers['Content-Type'] = 'application/json'
            return response

        with SQLAlchemySession(self.engine) as session:
            student = session.query(Student).get(id)
            if student is None:
                # do someting
                result = {
                    'success': False,
                    'error': 'No such quizz'}
            elif getattr(student, 'completion_date') is not None:
                # do something
                result = {
                    'success': False,
                    'error': 'Already completed'}
            else:
                result = method(student)

        return make_response(result)(environ, start_response)
