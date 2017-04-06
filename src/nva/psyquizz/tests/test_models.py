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
    import pdb; pdb.set_trace()
    assert 1 == 1
