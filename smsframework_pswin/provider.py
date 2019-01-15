# -*- coding: utf-8 -*-

from smsframework import IProvider, exc
from . import error
from . import status
from .api import PswinHttpApi, PswinApiError

try:  # Py3
    from urllib.request import URLError, HTTPError
except ImportError:  # Py2
    from urllib2 import URLError, HTTPError


class PswinProvider(IProvider):
    """ PSWin provider """

    def __init__(self, gateway, name, user, password, hostname=None, https=False):
        """ Configure PSWin provider

            :param user: Account username
            :param password: Account password
            :param https: Use HTTPS for outgoing messages?
        """
        self.api = PswinHttpApi(user, password, hostname, https)
        super(PswinProvider, self).__init__(gateway, name)

    def send(self, message):
        """ Send a message

            :type message: smsframework.data.OutgoingMessage.OutgoingMessage
            :rtype: OutgoingMessage
            """
        # Parameters
        params = {}
        if message.src:
            params['SND'] = message.src
        # senderId overrides source number.
        if message.provider_options.senderId:
            params['SND'] = message.provider_options.senderId
        if message.provider_options.status_report:
            params['RCPREQ'] = 'Y'

        try:
            # Here we attempt to encode the message in iso-8859-1. Only if this fails,
            # we use the UCS2 encoding.
            # This approach tries to fit as many characters into one SMS message as possible
            body = message.body.encode('iso-8859-1')
        except UnicodeError:
            body = message.body.encode('utf-16-be')
            message.params(is_hex=True)

        params.update(message.provider_params)

        try:
            message.msgid = \
                self.api.sendmsg(message.dst, body, **params)
            return message

        except HTTPError as e:
            raise exc.MessageSendError(str(e))
        except URLError as e:
            raise exc.ConnectionError(str(e))
        except PswinApiError as e:
            raise error.PswinProviderError(e.code, str(e))

    def make_receiver_blueprint(self):
        """ Create the receiver blueprint

            We do it in a function as the SmsFramework user might not want
            receivers, consequently, has no reasons
            for installing Flask
        """
        from . import receiver
        return receiver.bp
