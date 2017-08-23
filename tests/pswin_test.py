# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

from flask import Flask
from requests import Response

from smsframework import Gateway, OutgoingMessage
from smsframework.providers import NullProvider
from smsframework_pswin import PswinProvider

from smsframework_pswin import error, status


class PswinProviderTest(unittest.TestCase):
    def setUp(self):
        # Gateway
        gw = self.gw = Gateway()
        gw.add_provider('null', NullProvider)  # provocation
        gw.add_provider('main', PswinProvider,
                        user='user', password='password')

        self.requests = []

        # Flask
        app = self.app = Flask(__name__)

        # Register receivers
        gw.receiver_blueprints_register(app, prefix='/a/b/')

    def _mock_response(self, status_code):
        """ Monkey-patch PswinHttpApi so it returns a predefined response """
        def _api_request(**params):
            self.requests.append(params)

            response = Response()
            response.status_code = status_code
            return response

        self.gw.get_provider('main').api._api_request = _api_request

    def test_blueprints(self):
        """ Test blueprints """
        self.assertEqual(
            self.gw.receiver_blueprints().keys(),
            ['main']
        )

    def test_send(self):
        """ Test message send """
        gw = self.gw

        # OK
        self._mock_response(200)
        message = OutgoingMessage('+123456', 'hey', provider='main')
        message = gw.send(message)
        self.assertEqual(message.msgid, None)

        # Should fail with E001
        self._mock_response(500)
        self.assertRaises(error.E001, gw.send,
                          OutgoingMessage('+123456',
                                          'hey',
                                          provider='main'))

        raise NotImplementedError(u'Missing test for iso-8859-1 encodable strings (include ææåØÆÅ)')
        raise NotImplementedError(u'Missing test for UTF-8 messages (👍)')

    def test_senderId(self):
        gw = self.gw

        self._mock_response(200)  # OK
        message = OutgoingMessage('+123456', 'hey', provider='main')
        message.options(senderId='Fake sender')
        gw.send(message)
        request = self.requests.pop()
        self.assertEqual('Fake sender', request['SND'])

    def test_receive_message(self):
        """ Test message receipt """

        # Message receiver
        messages = []

        def receiver(message):
            messages.append(message)

        self.gw.onReceive += receiver

        with self.app.test_client() as c:
            # Message 1: GET artificial
            res = c.get('/a/b/main/im'
                        '?REF=foobar'
                        '&SND=123'
                        '&RCV=456'
                        '&TXT=hello+there')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(messages), 1)
            message = messages.pop()
            self.assertEqual(message.provider, 'main')
            self.assertEqual(message.msgid, 'foobar')
            self.assertEqual(message.src, '123')
            self.assertEqual(message.dst, '456')
            self.assertEqual(message.body, 'hello there')

            # Message 2: GET real, non-unicode
            res = c.get('/a/b/main/im'
                        '?SND=380660000000'
                        '&RCV=491700000000'
                        '&TXT=Hi%2C+man'
                        '&REF=c6b1e0eb9d6b8d549621235aaf089a26')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(messages), 1)
            message = messages.pop()
            self.assertEqual(message.provider, 'main')
            self.assertEqual(message.msgid, 'c6b1e0eb9d6b8d549621235aaf089a26')
            self.assertEqual(message.src, '380660000000')
            self.assertEqual(message.dst, '491700000000')
            self.assertEqual(message.body, 'Hi, man')

            # Message 3: GET real, unicode
            res = c.get('/a/b/main/im'
                        '?SND=380660000000'
                        '&RCV=491700000000'
                        '&TXT=%D0%9F%D1%80%D0%B8%D0%B2%D0%B5%D1%82%2C%20%'
                        'D0%B6%D0%BE%D0%BF%D0%B0!'
                        '&REF=c6b1e0eb9d6b8d549621235aaf089a26')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(messages), 1)
            message = messages.pop()
            self.assertEqual(message.provider, 'main')
            self.assertEqual(message.msgid, 'c6b1e0eb9d6b8d549621235aaf089a26')
            self.assertEqual(message.src, '380660000000')
            self.assertEqual(message.dst, '491700000000')
            self.assertEqual(message.body, u'Привет, жопа!')

            # Message 4: POST real, unicode
            res = c.post('/a/b/main/im', data={
                "REF": 1, "SND": "123", "RCV": "456", "TXT": "Hei+p%e5+deg+%d8%d8%d8"
            })
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(messages), 1)
            message = messages.pop()
            self.assertEqual(message.provider, 'main')
            self.assertEqual(message.msgid, '1')
            self.assertEqual(message.src, '123')
            self.assertEqual(message.dst, '456')
            self.assertEqual(message.body, u'Hei på deg ØØØ')

            # Message 5: POST real, non-unicode
            res = c.post('/a/b/main/im', data={
                "SND": "380660000000",
                "RCV": "491700000000",
                "TXT": "Hi%2C+man",
                "REF": "c6b1e0eb9d6b8d549621235aaf089a26"
            })
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(messages), 1)
            message = messages.pop()
            self.assertEqual(message.provider, 'main')
            self.assertEqual(message.msgid, 'c6b1e0eb9d6b8d549621235aaf089a26')
            self.assertEqual(message.src, '380660000000')
            self.assertEqual(message.dst, '491700000000')
            self.assertEqual(message.body, 'Hi, man')

            # Message 6: POST real, unicode
            res = c.post('/a/b/main/im', data={
                "SND": "380660000000",
                "RCV": "491700000000",
                "TXT": "Привет,+жопа!",
                "REF": "c6b1e0eb9d6b8d549621235aaf089a26"
            })
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(messages), 1)
            message = messages.pop()
            self.assertEqual(message.provider, 'main')
            self.assertEqual(message.msgid, 'c6b1e0eb9d6b8d549621235aaf089a26')
            self.assertEqual(message.src, '380660000000')
            self.assertEqual(message.dst, '491700000000')
            self.assertEqual(message.body, u'Привет, жопа!')

    def test_receive_status(self):
        """ Test status receipt """

        # Status receiver
        statuses = []

        def receiver(status):
            statuses.append(status)

        self.gw.onStatus += receiver

        with self.app.test_client() as c:
            # Status 1: GET artificial, delivered
            res = c.get('/a/b/main/status'
                        '?RCV=123'
                        '&REF=456'
                        '&STATE=DELIVRD'
                        '&DELIVERYTIME=201507090000')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(statuses), 1)
            st = statuses.pop()
            self.assertEqual(st.msgid, '456')
            self.assertEqual(st.provider, 'main')
            self.assertEqual(st.status, status.Delivered.status)

            # Status 2: GET artificial, error
            res = c.get('/a/b/main/status'
                        '?RCV=123'
                        '&REF=456'
                        '&STATE=UNDELIV')
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(statuses), 1)
            st = statuses.pop()
            self.assertEqual(st.msgid, '456')
            self.assertEqual(st.provider, 'main')
            self.assertEqual(st.status, status.Undelivered.status)

            # Status 3: POST artificial, delivered
            res = c.post('/a/b/main/status', data={
                "RCV": "123",
                "REF": "456",
                "STATE": "DELIVRD",
                "DELIVERYTIME": "201507090000"
            })
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(statuses), 1)
            st = statuses.pop()
            self.assertEqual(st.msgid, '456')
            self.assertEqual(st.provider, 'main')
            self.assertEqual(st.status, status.Delivered.status)

            # Status 4: POST artificial, error
            res = c.post('/a/b/main/status', data={
                "RCV": "123",
                "REF": "456",
                "STATE": "UNDELIV"
            })
            self.assertEqual(res.status_code, 200)
            self.assertEqual(len(statuses), 1)
            st = statuses.pop()
            self.assertEqual(st.msgid, '456')
            self.assertEqual(st.provider, 'main')
            self.assertEqual(st.status, status.Undelivered.status)
