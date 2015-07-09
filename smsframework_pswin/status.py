""" Message status codes """

from smsframework.data import *


class PswinMessageStatus(MessageStatus):
    status_code = None
    status = '(UNKNOWN STATUS CODE)'

    @classmethod
    def from_code(cls, status_code, **kwargs):
        """ Instantiate one of subclasses by code

            :rtype: type
        """
        for C in cls.__subclasses__():
            if C.status_code == status_code:
                return C(**kwargs)
        return cls(**kwargs)


class Delivered(PswinMessageStatus):
    status_code = 'DELIVRD'
    status = 'Message was successfully delivered to destination'


class Expired(PswinMessageStatus):
    status_code = 'EXPIRED'
    status = 'Message validity period has expired'


class Deleted(PswinMessageStatus):
    status_code = 'DELETED'
    status = 'Message has been deleted'


class Undelivered(PswinMessageStatus):
    status_code = 'UNDELIV'
    status = 'The SMS was undeliverable'


class Accpeted(PswinMessageStatus):
    status_code = 'ACCEPTD'
    status = 'Message was accepted'


class Unknown(PswinMessageStatus):
    status_code = 'UNKNOWN'
    status = 'No information of delivery status available'


class Rejected(PswinMessageStatus):
    status_code = 'REJECTD'
    status = 'Message was rejected'


class Failed(PswinMessageStatus):
    status_code = 'FAILED'
    status = 'The SMS failed to be delivered because no operator accepted '
    'the message or due to internal Gateway error'


class Barred(PswinMessageStatus):
    status_code = 'BARRED'
    status = 'The receiver number is barred/blocked/not in use. Do not '
    'retry message, and remove number from any subscriber list'


class TemporarilyBlocked(PswinMessageStatus):
    status_code = 'BARREDT'
    status = 'The receiver number is temporarily blocked. May be an empty '
    'pre-paid account or a subscriber that has extended his credit limit'


class PremuimBlocked(PswinMessageStatus):
    status_code = 'BARREDC'
    status = 'The receiver has blocked for Premium (CPA) messages. '
    'Send a non-Premium message to inform the customer about this'


class AgeBlocked(PswinMessageStatus):
    status_code = 'BARREDA'
    status = 'The receiver could not receive the message because his/her age '
    'is below the specified AgeLimit'


class NotSupported(PswinMessageStatus):
    status_code = 'BARREDP'
    status = 'The receiver could not receive the message because '
    'he/she has a prepaid subscription that is not supported'


class ZeroBalance(PswinMessageStatus):
    status_code = 'ZEROBAL'
    status = 'The receiver has an empty prepaid account'


class ZeroBalanceOther(PswinMessageStatus):
    status_code = 'ZERO_BAL'
    status = 'The receiver has an empty prepaid account'


class InvalidNetwork(PswinMessageStatus):
    status_code = 'INV_NET'
    status = 'Invalid network. Receiver number is not '
    'recognized by the target operator'
