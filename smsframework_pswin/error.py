""" PSWin error codes """

from smsframework.exc import *


class PswinProviderError(ProviderError):
    """ Base class for PSWin errors

        The __new__ method provides factory behavior: on construct,
        it mutates to one of its subclasses.
    """
    code = None
    title = '(UNKNOWN ERROR CODE)'

    def __new__(cls, code, message=''):
        # Pick the appropriate class
        for E in cls.__subclasses__():
            if E.code == code:
                C = E
                break
        else:
            C = cls
        return super(PswinProviderError, cls).__new__(C, code, message)

    def __init__(self, code, message=''):
        self.code = code
        super(PswinProviderError, self).__init__(
            '#{}: {}: {}'.format(self.code, self.title, message)
        )


class E001(PswinProviderError, AuthError):
    code = 1
    title = 'Authentication Failed'
