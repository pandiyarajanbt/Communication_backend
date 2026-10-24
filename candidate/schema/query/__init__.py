import graphene
from graphene import relay

try:
    from graphene_django_cud.filter import DjangoFilterConnectionField
except ImportError:  # pragma: no cover
    from graphene_django.filter import DjangoFilterConnectionField

from candidate.models import Candidate, CandidateMessage
from candidate.schema.query.message import CandidateType, CandidateMessageType, _require_auth


class CandidateQuery(graphene.ObjectType):
    candidates = DjangoFilterConnectionField(CandidateType)
    candidate = graphene.Field(CandidateType, candidate_id=graphene.Int(required=True))
    candidate_messages = graphene.List(
        CandidateMessageType,
        candidate_id=graphene.Int(required=True),
    )
    node = relay.Node.Field()

    # def resolve_candidate(self, info, candidate_id):
    #     _require_auth(info)
    #     return Candidate.objects.filter(pk=candidate_id).first()

    # def resolve_candidate_messages(self, info, candidate_id):
    #     _require_auth(info)
    #     return CandidateMessage.objects.filter(candidate_id=candidate_id).order_by('-timestamp')