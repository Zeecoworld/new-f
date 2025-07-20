from response import response
from fme.models.user import User
from fme.helpers import swagger_data
from drf_yasg.utils import swagger_auto_schema
from fme.views.base import BaseAuthorizationView
from fme.serializers.authentication import UserStatusSerializer

class ChangeUserStatusView(BaseAuthorizationView):
    """
        This endpoint change user status by admin
    """
    @swagger_auto_schema(
        request_body=UserStatusSerializer,
        responses=swagger_data.doc_response('empty', 'User')
    )
    def post(self, request):
        resp = {'status':403, 'message':'Unauthorised access'}
        if request.user.role == User.Role.ADMIN:
            resp = {'status':400, 'message':'Unable to update user status'}
            serializer = UserStatusSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user_id = request.data['user_id']
                user = User.objects.filter(pk=user_id).update(**serializer.data)
                if user:
                    resp = {'status':200, 'message':'Successfully update user status'}
        return response(resp)
