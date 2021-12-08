# -*- coding: utf-8 -*-

import smtplib
import html2text
import functools
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


ENCODING = 'utf-8'


class SecureMailer:

    def __init__(self, host, from_, user=None, pwd=None, port="2525"):
        self.mailer = None
        self.host = host
        self.port = port
        self.username = user
        self.password = pwd
        self.emitter = from_

    def __enter__(self):
        server = smtplib.SMTP(self.host, self.port)
        server.set_debuglevel(True)

        # identify ourselves, prompting server for supported features
        server.ehlo()

        # If we can encrypt this session, do it
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()  # re-identify ourselves over TLS connection

        if self.username and self.password:
            server.login(self.username, self.password)

        self.mailer = server
        return functools.partial(server.sendmail, self.emitter)

    def __exit__(self, type, value, traceback):
        self.mailer.close()

    def prepare(self, to, subject, html, text, reply=None, callback=None):
        msg = MIMEMultipart('alternative')
        msg['From'] = self.emitter
        msg['To'] = to
        msg['Subject'] = subject
        msg['return-path'] = callback or reply or self.emitter
        msg['reply-to'] = reply or self.emitter
        msg.add_header('return-path', callback or reply or self.emitter)
        msg.set_charset(ENCODING)
        part1 = MIMEText(text.encode('utf-8'), 'plain')
        part1.set_charset(ENCODING)
        part2 = MIMEText(html, 'html')
        part2.set_charset(ENCODING)

        msg.attach(part1)
        msg.attach(part2)

        return msg

    def prepare_from_template(
            self, tpl, to, subject, namespace, reply=None, callback=None):
        html = tpl.substitute(**namespace)
        text = html2text.html2text(html.decode('utf-8'))
        return self.prepare(to, subject, html, text, reply, callback)
