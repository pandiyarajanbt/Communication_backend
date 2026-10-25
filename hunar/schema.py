import graphene

from candidate.schema.mutation.candidate import CreateCandidateMutation, DeleteCandidateMutation
from candidate.schema.mutation.messager import SendWhatsAppBulk, SendWhatsAppMessage
from candidate.schema.query import CandidateQuery
from users.schema import LoginUserMutation, RegisterUserMutation, SendOtpMutation


class Mutation(graphene.ObjectType):
    register_user = RegisterUserMutation.Field()
    login_user = LoginUserMutation.Field()
    send_otp = SendOtpMutation.Field()
    create_candidate = CreateCandidateMutation.Field()
    delete_candidate = DeleteCandidateMutation.Field()
    send_whatsapp_message = SendWhatsAppMessage.Field()
    send_whatsapp_bulk = SendWhatsAppBulk.Field()


class Query(CandidateQuery, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)