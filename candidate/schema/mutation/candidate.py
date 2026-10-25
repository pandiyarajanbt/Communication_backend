import graphene
from graphene_django_cud.mutations import DjangoCreateMutation, DjangoDeleteMutation

from candidate.models import Candidate
from candidate.schema.query.message import CandidateType


class CreateCandidateMutation(DjangoCreateMutation):
    class Meta:
        model = Candidate
        fields = (
            'full_name',
            'phone_number',
            'status',
            'last_message',
            'whatsapp_message_id',
        )
        optional_fields = (
            'status',
            'last_message',
            'whatsapp_message_id',
        )


class DeleteCandidateMutation(DjangoDeleteMutation):
    class Meta:
        model = Candidate
