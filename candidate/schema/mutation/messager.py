import json
import graphene

from candidate.models import Candidate, Status
from candidate.whatsapp import send_template, send_text
from candidate.schema.query.message import _require_auth, _dispatch, SendResultType, BulkItemType


class SendWhatsAppMessage(graphene.Mutation):
    """Send a WhatsApp message to ONE candidate."""

    class Arguments:
        candidate_id = graphene.Int(required=True)
        message = graphene.String()                      # free text (24h window only)
        template = graphene.String(default_value="hello_world")
        params = graphene.List(graphene.String)          # template variables {{1}}, {{2}}

    Output = SendResultType

    def mutate(self, info, candidate_id, message=None, template="hello_world", params=None):
        # _require_auth(info)

        try:
            candidate = Candidate.objects.get(pk=candidate_id)
        except Candidate.DoesNotExist:
            return SendResultType(ok=False, error="Candidate not found")

        result = _dispatch(candidate, message, template, params)
        candidate.refresh_from_db()
        return SendResultType(candidate=candidate, **result)


class SendWhatsAppBulk(graphene.Mutation):
    class Arguments:
        candidate_ids = graphene.List(graphene.Int)      
        message = graphene.String()
        template = graphene.String(default_value="hello_world")
        params = graphene.List(graphene.String)

    count = graphene.Int()
    success_count = graphene.Int()
    failed_count = graphene.Int()
    results = graphene.List(BulkItemType)

    def mutate(self, info, candidate_ids=None, message=None, template="hello_world", params=None):
        # _require_auth(info)

        if candidate_ids:
            candidates = Candidate.objects.filter(pk__in=candidate_ids)
        else:
            candidates = Candidate.objects.filter(status=Status.NOT_SENT.value)

        results = []
        for c in candidates:
            r = _dispatch(c, message, template, params)
            results.append(BulkItemType(
                candidate_id=c.candidate_id,
                name=c.full_name,
                **r,
            ))

        success = sum(1 for r in results if r.ok)
        return SendWhatsAppBulk(
            count=len(results),
            success_count=success,
            failed_count=len(results) - success,
            results=results,
        )

