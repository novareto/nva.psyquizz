# -*- coding: utf-8 -*-


def test_simple(browser):
    page = browser('http://localhost/')
    assert "Startseite" in page.contents
