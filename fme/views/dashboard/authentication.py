from response import response
from fme.models.user import User
from rest_framework import views
from fme.helpers import swagger_data
from drf_yasg.utils import swagger_auto_schema
from fme.views.base import BaseAuthorizationView
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from fme.serializers.authentication import AuthenticateSerialize, UserSerializer

class LoginView(views.APIView):
    permission_classes = ()

    @swagger_auto_schema(
        request_body=AuthenticateSerialize,
        responses=swagger_data.doc_response('empty', 'User')
    )
    def post(self, request):
        resp, message = ({}, None)
        serializer = AuthenticateSerialize(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = authenticate(**serializer.data)
            if user:
                is_active = user.status != User.Status.DISABLED
                message = message if is_active else 'This account has been disabled.'
                if is_active:
                    login(request, user)
                    serialized = UserSerializer(user)
                    token, _ = Token.objects.get_or_create(user=user)
                    resp = {'status':200, 'data':{'token':token.key, **serialized.data}}
            else: message = 'Invalid email/password combination.'
            if message: resp = {'status':401, 'message':message}
        return response(resp)

class LogoutView(BaseAuthorizationView):

    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'User')
    )
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):pass
        logout(request)
        return response({'status':200, 'message':'User successfully logout'})
