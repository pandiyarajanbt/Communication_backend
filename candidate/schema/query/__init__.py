import graphene
from candidate.models import Candidate, Status
from candidate.schema.query.message import CandidateType, _require_auth


class CandidateQuery(graphene.ObjectType):
    candidates = graphene.List(CandidateType, status=graphene.String())
    candidate = graphene.Field(CandidateType, candidate_id=graphene.Int(required=True))

    def resolve_candidates(self, info, status=None):
        _require_auth(info)
        qs = Candidate.objects.all()
        if status:
            qs = qs.filter(status=status)
        return qs

    def resolve_candidate(self, info, candidate_id):
        _require_auth(info)
        return Candidate.objects.filter(pk=candidate_id).first()