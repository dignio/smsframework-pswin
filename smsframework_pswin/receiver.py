# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Blueprint, abort
from flask.globals import request, g

from smsframework.data import IncomingMessage
from .status import PswinMessageStatus


bp = Blueprint('smsframework-pswin', __name__, url_prefix='/')


def _merge_request(request):
    """ Merge query string and form body """
    data = {}
    data.update(request.form.to_dict())
    data.update(request.args.to_dict())
    return data


@bp.route('/im', methods=['GET', 'POST'])
def im():
    """ Incoming message handler

        PSWin sends data with POST:
        * RCV: Receiver number
        * SND: Sender number
        * TXT: Message data
        * REF: Delivery report reference
    """
    # PSWin doesn't actually use unicode; so tell flask to use the proper charset when decoding values
    request.charset = 'iso-8859-1'

    # Merge GET and POST
    req = _merge_request(request)

    # Check fields
    required_fields = ('RCV', 'SND', 'TXT')
    for field in required_fields:
        if field not in req:
            abort(400, 'PSWin sent a message with missing "{}" field'.format(field))

    # Parse date
    rtime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # IncomingMessage
    message = IncomingMessage(
        src=req['SND'],
        body=req['TXT'],
        msgid=req.get('REF'),
        dst=req['RCV'],
        rtime=rtime,
        meta=dict(NET=req.get('NET', None))
    )

    # Process it
    provider = g.provider  # yes, this is how the current provider is fetched
    " :type: smsframework.IProvider.IProvider "
    provider._receive_message(message)  # any exceptions will respond with 500

    # Ack
    return 'OK'


@bp.route('/status', methods=['GET', 'POST'])
def status():
    """ Incoming status report

        PSWin sends data with POST:
        * RCV: Receiver number
        * REF: Delivery report reference
        * STATE: State of message. Only the value 'DELIVRD'
                 should be considered a positive delivery acknowledgement.
        * DELIVERYTIME: Time of message delivery (yyyyMMddHHmm always in CET)
    """
    # PSWin doesn't actually use unicode; so tell flask to use the proper charset when decoding values
    request.charset = 'iso-8859-1'

    # Merge GET & POST
    req = _merge_request(request)

    # Check fields
    for n in ('RCV', 'REF', 'STATE'):
        assert n in req, 'PSWin sent a status with missing "{}" field: {}'\
                         .format(n, req)

    # MessageStatus
    status = PswinMessageStatus.from_code(
        req['STATE'],
        msgid=req['REF']
    )

    # Process it
    g.provider._receive_status(status)  # exception respond with http 500

    # Ack
    return 'OK'
