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

    link = page.getLink('Betrieb anlegen')
    link.click()
    assert "Unternehmen anlegen"

    form = page.getForm()
    form.getControl(name='form.field.name').value="Novareto GmbH"
    form.getControl(name='form.field.mnr').value="12345678"
    form.submit(name='form.action.add')
    
    assert "Novareto" in page.contents

    #link = page.getLink('(Neue Befragung anlegen)')
    #link.click()

    # Going on the graphic / stats page
    link = page.getLink('Grafische Darstellung')
    link.click()

    # Check the only answer averages
    assert '''["Vielseitiges Arbeiten", "4.00"]''' in page.contents
    assert '''["Ganzheitliches Arbeiten", "5.00"]''' in page.contents
    assert '''["Passende inhaltliche Arbeitsanforderungen", "4.50"]''' in page.contents
    assert '''["Passende mengenm\u00e4\u00dfige Arbeit", "4.00"]''' in page.contents
    assert '''["Passende Arbeitsabl\u00e4ufe", "1.00"]''' in page.contents
    assert '''["Passende Arbeitsumgebung", "1.50"]''' in page.contents
    assert '''["Handlungsspielraum", "3.67"]''' in page.contents
    assert '''["Soziale R\u00fcckendeckung", "5.00"]''' in page.contents
    assert '''["Zusammenarbeit", "3.00"]''' in page.contents
    assert '''["Information und Mitsprache", "1.00"]''' in page.contents
    assert '''["Entwicklungsm\u00f6glichkeiten", "1.00"]''' in page.contents


    # Logging out
    link = page.getLink('Abmelden')
    link.click()

    # Going to the completed student quizz page
    page = browser('http://localhost/quizz/ABCD')
    
    # Test for
    # "This quizz is already completed and therefore closed."
    # But it's not yet translated FIXME Christian
    
    # Going to the completed student quizz page
    page = browser('http://localhost/quizz/EFGH')

    # Complete the form
    form = page.getForm()
    form.getControl(name='form.field.question1').value="1"
    form.getControl(name='form.field.question2').value="2"
    form.getControl(name='form.field.question3').value="4"
    form.getControl(name='form.field.question4').value="5"
    form.getControl(name='form.field.question5').value="5"
    form.getControl(name='form.field.question6').value="5"
    form.getControl(name='form.field.question7').value="4"
    form.getControl(name='form.field.question8').value="3"
    form.getControl(name='form.field.question9').value="3"
    form.getControl(name='form.field.question10').value="2"
    form.getControl(name='form.field.question11').value="5"
    form.getControl(name='form.field.question12').value="1"
    form.getControl(name='form.field.question13').value="2"
    form.getControl(name='form.field.question14').value="3"
    form.getControl(name='form.field.question15').value="3"
    form.getControl(name='form.field.question16').value="3"
    form.getControl(name='form.field.question17').value="2"
    form.getControl(name='form.field.question18').value="5"
    form.getControl(name='form.field.question19').value="5"
    form.getControl(name='form.field.question20').value="5"
    form.getControl(name='form.field.question21').value="3"
    form.getControl(name='form.field.question22').value="2"
    form.getControl(name='form.field.question23').value="1"
    form.getControl(name='form.field.question24').value="1"
    form.getControl(name='form.field.question25').value="3"
    form.getControl(name='form.field.question26').value="5"
    form.getControl(name='form.field.extra_question1').value="False"

    # Submit the answer
    form.submit(name="form.action.answer")
    assert 'Vielen Dank für Ihre Teilnahme. Ihre Angaben wurden gespeichert.' in page.contents

    # Logging in
    page = browser('http://localhost/')
    form = page.getForm()
    form.getControl(name="username").value = "ck@novareto.de"
    form.getControl(name="password").value = "my new password"
    form.submit("Anmelden")

    link = page.getLink('Grafische Darstellung')
    link.click()
    
    # Check the new answer averages
    assert '''["Vielseitiges Arbeiten", "3.17"]''' in page.contents
    assert '''["Ganzheitliches Arbeiten", "5.00"]''' in page.contents
    assert '''["Passende inhaltliche Arbeitsanforderungen", "4.50"]''' in page.contents
    assert '''["Passende mengenm\u00e4\u00dfige Arbeit", "3.50"]''' in page.contents
    assert '''["Passende Arbeitsabl\u00e4ufe", "2.25"]''' in page.contents
    assert '''["Passende Arbeitsumgebung", "1.50"]''' in page.contents
    assert '''["Handlungsspielraum", "3.33"]''' in page.contents
    assert '''["Soziale R\u00fcckendeckung", "4.50"]''' in page.contents
    assert '''["Zusammenarbeit", "3.17"]''' in page.contents
    assert '''["Information und Mitsprache", "1.00"]''' in page.contents
    assert '''["Entwicklungsm\u00f6glichkeiten", "2.50"]''' in page.contents
