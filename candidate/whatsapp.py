import requests
from django.conf import settings
from django.utils import timezone
from .models import Candidate, CandidateMessage, Status


def _url():
    return (
        f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/"
        f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    )


def _headers():
    return {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }


def send_template(candidate: Candidate, template_name="hello_world", lang="en_US", params=None):
    """Send an approved template message to one candidate."""
    template = {"name": template_name, "language": {"code": lang}}

    # Optional: fill {{1}}, {{2}} variables in your template
    if params:
        template["components"] = [{
            "type": "body",
            "parameters": [{"type": "text", "text": p} for p in params],
        }]

    payload = {
        "messaging_product": "whatsapp",
        "to": candidate.phone_number,
        "type": "template",
        "template": template,
    }
    return _send(candidate, payload)


def send_text(candidate: Candidate, body: str):
    """Free-form text. Only works within 24h of the candidate's last reply."""
    payload = {
        "messaging_product": "whatsapp",
        "to": candidate.phone_number,
        "type": "text",
        "text": {"body": body},
    }
    return _send(candidate, payload)


def _message_text(payload):
    if payload.get("type") == "text":
        return payload.get("text", {}).get("body") or "WhatsApp text message"
    if payload.get("template"):
        template_name = payload.get("template", {}).get("name")
        if template_name:
            return f"Template: {template_name}"
    return "WhatsApp message"


def _send(candidate, payload):
    message_text = _message_text(payload)

    try:
        resp = requests.post(_url(), json=payload, headers=_headers(), timeout=15)
        data = resp.json()
    except requests.RequestException as e:
        candidate.status = Status.FAILED.value
        candidate.save(update_fields=["status"])
        CandidateMessage.objects.create(
            candidate=candidate,
            message_id="",
            message=message_text,
            status=Status.FAILED.value,
        )
        return {"ok": False, "error": str(e)}

    if resp.status_code == 200 and "messages" in data:
        candidate.status = Status.SEND.value
        candidate.whatsapp_message_id = data["messages"][0]["id"]
        candidate.last_message = timezone.now()
        candidate.save(update_fields=["status", "whatsapp_message_id", "last_message"])
        CandidateMessage.objects.create(
            candidate=candidate,
            message_id=candidate.whatsapp_message_id,
            message=message_text,
            status=Status.SEND.value,
        )
        return {"ok": True, "message_id": candidate.whatsapp_message_id}

    candidate.status = Status.FAILED.value
    candidate.save(update_fields=["status"])
    CandidateMessage.objects.create(
        candidate=candidate,
        message_id="",
        message=message_text,
        status=Status.FAILED.value,
    )
    return {"ok": False, "error": data.get("error", data)}