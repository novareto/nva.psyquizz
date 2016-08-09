# -*- coding: utf-8 -*-

import smtplib
import time
from string import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


ENCODING = 'utf-8'


class SecureMailer(object):

    def __init__(self, host, username=None, password=None, port="25"):
        self.mailer = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def __enter__(self):
        server = smtplib.SMTP(self.host, self.port)
        server.set_debuglevel(True)

        # identify ourselves, prompting server for supported features
        server.ehlo()

        # If we can encrypt this session, do it
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo() # re-identify ourselves over TLS connection

        if self.username and self.password:
            server.login(self.username, self.password)

        self.mailer = server
        return server.sendmail

    def __exit__(self, type, value, traceback):
        self.mailer.close()


def prepare(emitter, recipient, subject, html, text, reply=None, callback=None):
    msg = MIMEMultipart('alternative')
    msg['From'] = emitter
    msg['To'] = recipient
    msg['Subject'] = subject
    msg['return-path'] = callback or reply or emitter
    msg['reply-to'] = reply or emitter
    msg.add_header('return-path', callback or reply or emitter)
    msg.set_charset(ENCODING)

    part1 = MIMEText(text, 'plain')
    part1.set_charset(ENCODING)
    part2 = MIMEText(html, 'html')
    part2.set_charset(ENCODING)

    msg.attach(part1)
    msg.attach(part2)

    return msg
