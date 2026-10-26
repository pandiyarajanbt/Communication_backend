import json
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from twilio.rest import Client

from .models import Candidate, CandidateMessage, Status


def _normalize_whatsapp_number(value):
    value = str(value or '').strip()
    if not value:
        raise ValueError('Phone number is required')
    if value.startswith('whatsapp:'):
        return value
    return f'whatsapp:{value}'


def _from_number():
    from_number = (settings.TWILIO_WHATSAPP_NUMBER or '').strip()
    if not from_number:
        raise RuntimeError('Twilio WhatsApp number is not configured')
    return from_number if from_number.startswith('whatsapp:') else f'whatsapp:{from_number}'


def _client():
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    if not account_sid or not auth_token:
        raise RuntimeError('Twilio credentials are not configured')
    return Client(account_sid, auth_token)


def send_template(candidate: Candidate, template_name="hello_world", lang="en_US", params=None):
    template_sid = getattr(settings, 'TWILIO_WHATSAPP_TEMPLATE_SID', '')
    template_sid = str(template_sid or '').strip()

    if template_sid:
        variables = {}
        if params:
            for index, value in enumerate(params, start=1):
                variables[str(index)] = value
        payload = {
            'content_sid': template_sid,
            'from_': _from_number(),
            'to': _normalize_whatsapp_number(candidate.phone_number),
            'content_variables': json.dumps(variables),
        }
        return _send(candidate, payload, message_text=f'Template: {template_name}')

    safe_message = template_name if isinstance(template_name, str) and template_name else 'Hello from Twilio'
    if params:
        safe_message = ' '.join(str(value) for value in params)
    return send_text(candidate, safe_message)


def _has_active_whatsapp_window(candidate: Candidate, hours: int = 24) -> bool:
    if not candidate.last_message:
        return False
    return timezone.now() - candidate.last_message <= timedelta(hours=hours)


def send_text(candidate: Candidate, body: str):
    """Send a free-form WhatsApp text message through Twilio."""
    payload = {
        'body': body,
        'from_': _from_number(),
        'to': _normalize_whatsapp_number(candidate.phone_number),
    }
    return _send(candidate, payload, message_text=body)


def _message_text(payload):
    if payload.get('body'):
        return payload.get('body')
    if payload.get('content_sid'):
        return f"Template: {payload.get('content_sid')}"
    return 'Twilio WhatsApp message'


def _send(candidate, payload, message_text=None):
    message_text = message_text or _message_text(payload)

    try:
        message = _client().messages.create(**payload)
    except Exception as e:
        candidate.status = Status.FAILED.value
        candidate.save(update_fields=['status'])
        CandidateMessage.objects.create(
            candidate=candidate,
            message_id='',
            message=message_text,
            status=Status.FAILED.value,
        )
        return {'ok': False, 'error': str(e)}

    candidate.status = Status.SEND.value
    candidate.whatsapp_message_id = getattr(message, 'sid', '')
    candidate.last_message = timezone.now()
    candidate.save(update_fields=['status', 'whatsapp_message_id', 'last_message'])
    CandidateMessage.objects.create(
        candidate=candidate,
        message_id=candidate.whatsapp_message_id,
        message=message_text,
        status=Status.SEND.value,
    )
    return {'ok': True, 'message_id': candidate.whatsapp_message_id}
