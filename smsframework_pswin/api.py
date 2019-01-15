# -*- coding: utf-8 -*-

import requests
import binascii

# Content types, https://wiki.pswin.com/Message%20types.ashx
CT_PLAIN_TEXT = 1
CT_UCS2 = 9


class PswinApiError(RuntimeError):
    def __init__(self, code, message):
        self.code = code
        super(PswinApiError, self).__init__(message)


class PswinHttpApi(object):
    """ PSWin HTTP API client """

    def __init__(self, user, password, hostname=None, https=False):
        """ Create an authenticated client
            :type https: bool
            :param https: Use HTTPS protocol for requests?
        """
        self._auth = dict(
            USER=user,
            PW=password
        )
        self._https = https
        self._hostname = hostname or 'simple.pswin.com'

    def _api_request(self, **params):
        """ Make an API request and return the response
            :rtype: requests.Response
        """
        url = '{protocol}://{host}/'.format(
            protocol='https' if self._https else 'http',
            host=self._hostname
        )

        payload = {}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload.update(self._auth)
        payload.update(params)
        res = requests.post(url, data=payload, headers=headers)

        return res

    def api_request(self, **params):
        """ Make a custom request to PSWin and get the response object. """
        response = self._api_request(**params)
        if response.status_code == 200:
            # Success
            return response
        else:
            # Raise correct error
            raise PswinApiError(code=1, message='ERROR')

    def sendmsg(self, to, text, **params):
        """ Send SMS message """
        params['RCV'] = to
        if params.get('is_hex', False):
            params['HEX'] = binascii.hexlify(text)
            params['CT'] = CT_UCS2
        else:
            params['TXT'] = text
            params['CT'] = CT_PLAIN_TEXT
        response = self.api_request(**params)
        # TODO: analyze response, see if everything went well
