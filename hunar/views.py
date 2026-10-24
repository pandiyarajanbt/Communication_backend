from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from graphene_file_upload.django import FileUploadGraphQLView


@method_decorator(csrf_exempt, name="dispatch")
class CustomGraphQLView(FileUploadGraphQLView):
    graphiql_template = "graphiql_old.html"