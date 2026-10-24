import requests
from django.conf import settings
from django.utils import timezone
from .models import Candidate, Status


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


def _send(candidate, payload):
    try:
        resp = requests.post(_url(), json=payload, headers=_headers(), timeout=15)
        data = resp.json()
    except requests.RequestException as e:
        candidate.status = Status.FAILED.value
        candidate.save(update_fields=["status"])
        return {"ok": False, "error": str(e)}

    if resp.status_code == 200 and "messages" in data:
        candidate.status = Status.SEND.value
        candidate.whatsapp_message_id = data["messages"][0]["id"]
        candidate.last_message = timezone.now()
        candidate.save(update_fields=["status", "whatsapp_message_id", "last_message"])
        return {"ok": True, "message_id": candidate.whatsapp_message_id}

    candidate.status = Status.FAILED.value
    candidate.save(update_fields=["status"])
    return {"ok": False, "error": data.get("error", data)}