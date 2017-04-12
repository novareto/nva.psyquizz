# -*- coding: utf-8 -*-

from nva.psyquizz.models import Account


def test_simple(session_with_content, browser):
    transaction, session = session_with_content
    
    # Get the frontpage
    page = browser('http://localhost/')
    assert "Startseite" in page.contents

    # Make sure the account is there
    account = session.query(Account).get('ck@novareto.de')
    assert account.email == "ck@novareto.de"

    # Login
    form = page.getForm()
    form.getControl(name="username").value = "ck@novareto.de"
    form.getControl(name="password").value = "TEST"
    form.submit("Anmelden")

    # Make sure we are logged in
    assert 'Mein Profil' in page.contents

    link = page.getLink('Mein Profil')
    link.click()
    print page.contents
