""" swagger schema generator helper """
import os
from drf_yasg import openapi
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator

class SchemaGenerator(OpenAPISchemaGenerator):
    """ schema generator class """
    def get_schema(self, request=None, public=False):
        """ get doc schema """
        schema = super(SchemaGenerator, self).get_schema(request, public)
        schema.basePath = os.path.join(schema.basePath, 'api/')
        return schema

def run_get_schema_view(documented_urls):
    """ for get_schema_view """
    return get_schema_view(
        openapi.Info(
            title="FME API",
            default_version='v1',
            description="FME coursera",
            terms_of_service=settings.FME_TERMS_OF_SERVICE_URL,
            contact=openapi.Contact(email=settings.FME_EMAIL),
            license=openapi.License(name=settings.FME_DOC_LICENCE_TYPE),
        ),
        public=True,
        patterns=documented_urls,
        permission_classes=(permissions.AllowAny,),
        generator_class=SchemaGenerator,
    )
