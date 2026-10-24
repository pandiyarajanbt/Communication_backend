import graphene

from users.schema import LoginUserMutation, RegisterUserMutation, SendOtpMutation


class Mutation(graphene.ObjectType):
    register_user = RegisterUserMutation.Field()
    login_user = LoginUserMutation.Field()
    send_otp = SendOtpMutation.Field()


class Query(graphene.ObjectType):
    ping = graphene.String()

    def resolve_ping(self, info):
        return "ok"


schema = graphene.Schema(query=Query, mutation=Mutation)