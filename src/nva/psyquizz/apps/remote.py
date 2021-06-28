# -*- coding: utf-8 -*-

import json
import webob
from routes import Mapper
from cromlech.webob import Response
from cromlech.sqlalchemy import SQLAlchemySession
from ..models import Account, Company


routes = Mapper()


def route(path, methods=None):
    if methods is None:
        methods = ['GET']
    def wrapper(func):
        routes.connect(
            path, controller=func, action=func.__name__,
            conditions=dict(method=methods))
        return func
    return wrapper


@route('/company/{id:\d+}')
def get_company(engine, environ, id=None):
    with SQLAlchemySession(engine) as session:
        company = session.query(Company).get(int(id))
        if company is None:
            result = {
                'success': False,
                'error': 'Unknown company'}
        else:
            result = {
                'success': True,
                'data': {'name': company.name},
            }
    return result


@route('/account/{email}')
def get_account(engine, environ, email=None):
    with SQLAlchemySession(engine) as session:
        account = session.query(Account).get(email)
        if account is None:
            result = {
                'success': False,
                'error': 'Unknown account',
            }
        else:
            result = {
                'success': True,
                'data': {'name': account.name},
            }
    return result


class Application:

    def __init__(self, configuration):
        self.engine = configuration.engine

    def __call__(self, environ, start_response):

        routing = routes.match(environ=environ)
        if routing is not None:
            routing.pop('action', None)
            handler = routing.pop('controller')
            jresult = handler(self.engine, environ, **routing)
        else:
            return webob.exc.HTTPNotFound()(environ, start_response)


        def make_response(result):
            json_result = json.dumps(result)
            response = Response()
            response.write(json_result)
            response.headers['Content-Type'] = 'application/json'
            return response

        return make_response(jresult)(environ, start_response)
