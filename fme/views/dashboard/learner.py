from response import response
from django.conf import settings
from fme.helpers import swagger_data
from fme.models.learner import LearnerProfile
from drf_yasg.utils import swagger_auto_schema
from fme.views.base import BaseAuthenticationView
from fme.helpers.pagination import PaginationHandlerMixin
from fme.serializers.base import PaginationParamSerializer
from fme.serializers.learner import LearnerProfileSerializer

class ListLearnerView(BaseAuthenticationView, PaginationHandlerMixin):
    """
        This endpoint get paginated list of learner profile
    """
    @swagger_auto_schema(
        query_serializer=PaginationParamSerializer,
        responses=swagger_data.doc_response('list_learner_data', 'LearnerProfile')
    )
    def get(self, request):
        parsed_params = PaginationParamSerializer(data=request.query_params)
        parsed_params.is_valid(raise_exception=True)
        parsed_params = parsed_params.data
        learner_qs = LearnerProfile.objects.all()
        self.page_size = parsed_params.get('page_size', settings.DEFAULT_PAGINATION_SIZE)
        paginate_qs = self.paginate_queryset(learner_qs, request, view=self)
        learner_serializer = LearnerProfileSerializer(paginate_qs, many=True).data
        if learner_serializer:
            return response(
                {"status": 200, "data": self.get_paginated_response(learner_serializer)}
            )
        return response({"status": 400, "message": "Record not found"})
