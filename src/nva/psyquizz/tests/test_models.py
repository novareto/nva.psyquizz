# -*- coding: utf-8 -*-

from nva.psyquizz.models.account import Account


def test_one(dbsession):
    account = Account(
        email="ck@novareto.de",
        name="Christian Klinger",
        password="TEST",
        activation="BLA"
    )
    dbsession.add(account)
    dbsession.query(Account).get('ck@novareto.de')


def test_two(session_with_content):
    assert session_with_content.query(Account).get('ck@novareto.de') is not None
    assert session_with_content.query(Account).get('trollfot@novareto.de') is None

