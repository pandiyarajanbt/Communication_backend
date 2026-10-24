import json

import graphene
from graphene_django import DjangoObjectType

from candidate.models import Candidate
from candidate.whatsapp import send_template, send_text


# ---------- Types ----------

class CandidateType(DjangoObjectType):
    class Meta:
        model = Candidate
        fields = "__all__"
        convert_choices_to_enum = False  # return status as a plain string


class SendResultType(graphene.ObjectType):
    ok = graphene.Boolean()
    message_id = graphene.String()
    error = graphene.String()
    candidate = graphene.Field(CandidateType)


class BulkItemType(graphene.ObjectType):
    candidate_id = graphene.Int()
    name = graphene.String()
    ok = graphene.Boolean()
    message_id = graphene.String()
    error = graphene.String()


# ---------- Helpers ----------

def _require_auth(info):
    user = getattr(info.context, "user", None)
    if not user or not user.is_authenticated:
        raise Exception("Authentication required")


def _dispatch(candidate, message, template, params):
    """Send free text if message given, otherwise a template."""
    if message:
        result = send_text(candidate, message)
    else:
        result = send_template(candidate, template_name=template, params=params)

    error = result.get("error")
    if error is not None and not isinstance(error, str):
        error = json.dumps(error)

    return {
        "ok": result["ok"],
        "message_id": result.get("message_id"),
        "error": error,
    }






