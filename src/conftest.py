# -*- coding: utf-8 -*-

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--zcml", action="store", default=None)


@pytest.fixture(scope='session')
def zcml(request):
    return request.config.getoption("--zcml")
