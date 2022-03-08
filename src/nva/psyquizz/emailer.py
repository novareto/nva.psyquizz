# -*- coding: utf-8 -*-

import os
import logging
import transaction
import smtplib
import html2text
import functools
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randrange
from time import strftime
from socket import gethostname
from typing import NamedTuple, Type
from contextlib import contextmanager
from transaction.interfaces import (
    ISavepointDataManager, IDataManagerSavepoint)
from zope.interface import implementer


ENCODING = 'utf-8'


@implementer(ISavepointDataManager)
class MailDataManager:

    def __init__(self, callable, vote=None, onAbort=None):
        self.callable = callable
        self.vote = vote
        self.onAbort = onAbort
        # Use the default thread transaction manager.
        self.transaction_manager = transaction.manager

    def commit(self, txn):
        pass

    def abort(self, txn):
        if self.onAbort:
            self.onAbort()

    def sortKey(self):
        return str(id(self))

    def savepoint(self):
        pass

    def abort_sub(self, txn):
        pass

    commit_sub = abort_sub

    def beforeCompletion(self, txn):
        pass

    afterCompletion = beforeCompletion

    def tpc_begin(self, txn, subtransaction=False):
        assert not subtransaction

    def tpc_vote(self, txn):
        if self.vote is not None:
            return self.vote()

    def tpc_finish(self, txn):
        try:
            self.callable()
        except Exception as exc:
            # Any exceptions here can cause database corruption.
            # Better to protect the data and potentially miss emails than
            # leave a database in an inconsistent state which requires a
            # guru to fix.
            log.exception("Failed in tpc_finish for %r", self.callable)

    tpc_abort = abort


class MailDelivery:

    def __init__(self, mailer):
        self.mailer = mailer
        self.queue = []
        self.txn = None

    def vote(self):
        server = smtplib.SMTP(
            self.mailer.host, str(self.mailer.port))

        code, response = server.ehlo()
        if code < 200 or code >= 300:
            code, response = server.helo()
            if code < 200 or code >= 300:
                raise RuntimeError(
                    'Error sending HELO to the SMTP server '
                    f'(code={code}, response={response})'
                )

    def commit(self):
        server = smtplib.SMTP(
            self.mailer.host, self.mailer.port)
        server.set_debuglevel(self.mailer.debug)

        # identify ourselves, prompting server for supported features
        server.ehlo()

        # If we can encrypt this session, do it
        if server.has_extn("STARTTLS"):
            server.starttls()
            server.ehlo()  # re-identify ourselves over TLS connection
        if self.mailer.username:
            server.login(
                self.mailer.username,
                self.mailer.password
            )
        try:
            for email in self.queue:
                server.send_message(email)
        finally:
            server.close()

    def abort(self):
        self.queue.clear()
        self.datamanager = None

    def email(self, recipient, subject, text, html=None):
        message = self.mailer.prepare(recipient, subject, text, html)
        return self(message)

    def __call__(self, message):
        if self.txn is None:
            self.txn = transaction.get()
            if self.txn.isDoomed():
                raise RuntimeError(
                    'The transaction is doomed, no more emailing.')

            self.txn.join(MailDataManager(
                self.commit,
                vote=self.vote,
                onAbort=self.abort
            ))
        self.queue.append(message)
        return message['Message-ID']


class SecureMailer:

    delivery = MailDelivery

    def __init__(self, host, from_, user=None, pwd=None, port="2525"):
        self.host = host
        self.port = port
        self.username = user
        self.password = pwd
        self.emitter = from_

    @classmethod
    def new_message_id(self):
        randmax = 0x7fffffff
        left_part = '%s.%d.%d' % (strftime('%Y%m%d%H%M%S'),
                                  os.getpid(),
                                  randrange(0, randmax))
        return "%s@%s" % (left_part, gethostname())

    def prepare(self, to, subject, text, html, reply=None, callback=None):
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

    def get_sender(self):
        return MailDelivery(self)
