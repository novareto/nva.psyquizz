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
    assert 'Christian Klinger' in page.contents
    assert 'Novareto' in page.contents
    assert 'Crash Course' in page.contents

    # We have 1 answer in the Crash Course session
    assert '<span> Die Auswertung wird erst ab dem <b> <span>1</span>.</b> ausgefüllten Fragebogen angzeigt </span>'

    # Checking the profile management
    link = page.getLink('Mein Profil')
    link.click()

    # changing the password and validating
    form = page.getForm()
    form.getControl(name='form.field.password').value = "my new password"
    form.submit("Aktualisieren")

    # unlogging
    link = page.getLink('Abmelden')
    link.click()

    # Asserting we are now unlogged
    assert 'Mein Profil' not in page.contents
    
    # Logging in with the new password
    form = page.getForm()
    form.getControl(name="username").value = "ck@novareto.de"
    form.getControl(name="password").value = "my new password"
    form.submit("Anmelden")

    # Checking the new logging was successful
    assert 'Mein Profil' in page.contents
    assert 'Christian Klinger' in page.contents
    assert 'Novareto' in page.contents
    assert 'Crash Course' in page.contents
