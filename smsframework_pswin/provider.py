from smsframework import IProvider, exc
from . import error
from . import status
from .api import PswinHttpApi, PswinApiError
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
        params.update(message.provider_params)

        try:
            message.body = message.body.encode('iso-8859-1')
            message.params(CT=1)
        except UnicodeError:
            message.params(is_hex=True, CT=9)

        try:
            message.msgid = \
                self.api.sendmsg(message.dst, message.body, **params)
            return message

        except HTTPError as e:
            raise exc.MessageSendError(e.message)
        except URLError as e:
            raise exc.ConnectionError(e.message)
        except PswinApiError as e:
            raise error.PswinProviderError(e.code, e.message)

    def make_receiver_blueprint(self):
        """ Create the receiver blueprint

            We do it in a function as the SmsFramework user might not want
            receivers, consequently, has no reasons
            for installing Flask
        """
        from . import receiver
        return receiver.bp
