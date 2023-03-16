# -*- coding: utf-8 -*-

import os
import logging
import transaction
import smtplib
import html2text
import functools
from ssl import SSLError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randrange
from time import strftime
from socket import gethostname
from contextlib import contextmanager
from transaction.interfaces import IDataManager
from zope.interface import implementer


ENCODING = 'utf-8'


@implementer(IDataManager)
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
        pass

    def sortKey(self):
        return str(id(self))

    def tpc_abort(self, txn):
        if self.onAbort:
            self.onAbort()

    def tpc_begin(self, txn, subtransaction=False):
        assert not subtransaction

    def tpc_vote(self, txn):
        try:
            if self.vote is not None:
                return self.vote()
        except Exception as exc:
            raise RuntimeError(
                'An error occured while trying to reach the '
                'email server: %s' % exc
            )

    def tpc_finish(self, txn):
        try:
            self.callable()
        except Exception as exc:
            # Any exceptions here can cause database corruption.
            # Better to protect the data and potentially miss emails than
            # leave a database in an inconsistent state which requires a
            # guru to fix.
            logging.exception(
                "Failed in tpc_finish for %r", self.callable)


class MailDelivery:

    def __init__(self, mailer):
        self.mailer = mailer
        self.queue = []
        self.txn = None
        self.connection = None
        self.code = None
        self.response = None

    def server_is_available(self):
        if self.connection is None:
            self.connection = server = smtplib.SMTP(
                self.mailer.host, self.mailer.port
            )
            server.set_debuglevel(5)
            code, response = server.ehlo()
            if code < 200 or code >= 300:
                code, response = server.helo()
                if code < 200 or code >= 300:
                    self._close_connection()
                    raise RuntimeError(
                        'Error sending HELO to the SMTP server '
                        '(code=%s, response=%s)' % (code, response)
                    )
            self.code, self.response = code, response

    def _close_connection(self):
        if self.connection is not None:
            try:
                self.connection.quit()
            except SSLError:
                # something weird happened while quiting
                self.connection.close()
            self.connection = None

    def exhaust_queue(self):
        if not self.queue:
            return self._close_connection()

        if self.connection is None:
            self.server_is_available()

        connection = self.connection

        if connection.has_extn('starttls'):
            connection.starttls()
            connection.ehlo()
        if self.mailer.username:
            connection.login(
                self.mailer.username,
                self.mailer.password
            )
        try:
            for email in self.queue:
                connection.sendmail(
                    email['From'], email['To'], email.as_string())
        except Exception as exc:
            print(exc)  # can't raise.
        finally:
            self._close_connection()

    def abort_queue(self):
        del self.queue[:]
        self.datamanager = None
        if self.connection is None:
            return
        self._close_connection()

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
                self.exhaust_queue,
                vote=self.server_is_available,
                onAbort=self.abort_queue
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
        part2 = MIMEText(html.encode('utf-8'), 'html')
        part2.set_charset(ENCODING)

        msg.attach(part1)
        msg.attach(part2)

        return msg

    def prepare_from_template(
            self, tpl, to, subject, namespace, reply=None, callback=None):
        html = tpl.substitute(**namespace)
        text = html2text.html2text(html.decode('utf-8'))
        return self.prepare(to, subject, text, html, reply, callback)

    def get_sender(self):
        return MailDelivery(self)
