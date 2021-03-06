# -*- coding: utf-8 -*-

from nva.psyquizz.models.account import Account


def test_one(dbsession):
    transaction, session = dbsession
    
    account = Account(
        email="ck@novareto.de",
        name="Christian Klinger",
        password="TEST",
        activation="BLA"
    )
    session.add(account)
    session.query(Account).get('ck@novareto.de')


def test_two(session_with_content):
    transaction, session = session_with_content
    assert session.query(Account).get('ck@novareto.de') is not None
    assert session.query(Account).get('trollfot@novareto.de') is None

