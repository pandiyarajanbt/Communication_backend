import json

import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from candidate.models import Candidate, CandidateMessage
from candidate.whatsapp import send_template, send_text


class CandidateMessageType(DjangoObjectType):
    class Meta:
        model = CandidateMessage
        fields = "__all__"
        convert_choices_to_enum = False


class CandidateType(DjangoObjectType):
    messages = graphene.List(CandidateMessageType)

    class Meta:
        model = Candidate
        fields = "__all__"
        interfaces = (relay.Node,)
        filter_fields = {
            'candidate_id': ['exact'],
            'full_name': ['exact', 'icontains'],
            'phone_number': ['exact', 'icontains'],
            'status': ['exact', 'in'],
            'last_message': ['exact', 'gte', 'lte'],
            'timestamp': ['exact', 'gte', 'lte'],
        }
        convert_choices_to_enum = False  # return status as a plain string

    def resolve_messages(self, info):
        return self.messages.all().order_by('-timestamp')


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






