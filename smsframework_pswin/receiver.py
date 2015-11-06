import urllib
from datetime import datetime

from flask import Blueprint
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
    """
    req = _merge_request(request)

    # Check fields
    for n in ('RCV', 'SND', 'TXT'):
        assert n in req, 'PSWin sent a message with missing "{}" field: {}'\
                         .format(n, req)

    # Parse date
    rtime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Message encoding
    req['TXT'] = urllib.unquote_plus(req['TXT'])

    # IncomingMessage
    message = IncomingMessage(
        src=req['SND'],
        body=req['TXT'],  # CHECKME: test that unicode works
        dst=req['RCV'],
        rtime=rtime
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
