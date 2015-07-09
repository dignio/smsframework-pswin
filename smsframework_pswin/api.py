# -*- coding: utf-8 -*-
import requests
import re


class PswinApiError(RuntimeError):
    def __init__(self, code, message):
        self.code = code
        super(PswinApiError, self).__init__(message)


class PswinHttpApi(object):
    """ PSWin HTTP API client """

    def __init__(self, user, password, https=False):
        """ Create an authenticated client
            :type https: bool
            :param https: Use HTTPS protocol for requests?
        """
        self._auth = dict(
            USER=user,
            PW=password
        )
        self._https = https
        self._hostname = 'simple.pswin.com'

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
        params['TXT'] = text
        response = self.api_request(**params)
