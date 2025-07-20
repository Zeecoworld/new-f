import re
import secrets
from response import response
from django.conf import settings
from fme.views.base  import BaseView
from fme.helpers import swagger_data
from fme.models.learner import LearnerProfile
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authtoken.models import Token
from fme.models.nin import NinVerificationProcess
from fme.serializers.learner import CreateLearnerSerializer, CreateLearnerQueryParamSerializer
from fme.serializers.onbaording import (
    NinVerificationSerializer, NinFinalizeSerializer, NinTokenResendSerializer, NinDetailSerializer
)


class VerifyNinView(BaseView):
    """
        This endpoint start nin verification
    """
    dojah_nin_url = settings.DOJAH_NIN_VALIDATION_URL
    termii_sms_url = f'{settings.TERMII_SMS_BASE_URL}/api/sms/send'

    @swagger_auto_schema(
        request_body=NinVerificationSerializer,
        responses=swagger_data.doc_response('nin_verification_first_step', 'Nin')
    )
    def post(self, request):
        err_msg = None
        resp = {'status': 400, 'message':'Nin verification failed'}
        serializer = NinVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nin = serializer.data['nin']
        nin_v_process = NinVerificationProcess.objects.filter(nin=nin).first()
        data = {'message':'NIN verification process successfully started and OTP sent'}
        if nin_v_process:
            data['verification_id'] = nin_v_process.id
            if nin_v_process.user:resp = {'status':400, 'message':'User already exist'}
        else:
            nin_resp, err_msg = self.make_nin_request(self.dojah_nin_url, nin)
            if nin_resp and nin_resp.get('entity'):
                nin_entity = nin_resp['entity']
                nin_entity.pop('photo')
                phone_number = NinVerificationProcess.format_phone_number(nin_entity['phone_number'])
                # Generate a random five-digit number (1000 to 9999)
                token = f"{secrets.randbelow(9000) + 1000:05d}"
                _, err_msg = self.make_sms_request(self.termii_sms_url, phone_number, token)
                nin_v_process = NinVerificationProcess.objects.create(
                    nin_detail=nin_entity,
                    nin=nin, phone_number=phone_number, verification_token=token
                )
                data['verification_id'] = nin_v_process.id
        if err_msg: resp = {'status':400, 'message':err_msg}
        resp = {'status':200, 'data':data} if data.get('verification_id') else resp
        return response(resp)


class FinalizeNinVerificationView(BaseView):
    """
        This endpoint finalised nin verification
    """
    @swagger_auto_schema(
        request_body=NinFinalizeSerializer,
        responses=swagger_data.doc_response('nin_verification_final_step', 'Nin')
    )
    def post(self, request):
        resp = {'status': 404, 'message':'Nin verification token failed'}
        serializer = NinFinalizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.data
        verification_id = payload['verification_id']
        nin_v_process = NinVerificationProcess.objects.filter(id=verification_id).first()
        if nin_v_process:
            if nin_v_process.verification_token == payload['token']:
                NinVerificationProcess.objects.filter(id=verification_id).update(nin_is_verified=True)
                nin_detail = NinDetailSerializer(nin_v_process).data
                data = {
                    'nin_detail': nin_detail,
                    'verification_id':nin_v_process.id, 
                    'message':'Nin verification successfully completed'
                }
                resp = {'status':200, 'data':data}
        return response(resp)
    
class NinVerificationTokenResendView(BaseView):
    """
        This endpoint resent nin verification token
    """
    termii_sms_url = f'{settings.TERMII_SMS_BASE_URL}/api/sms/send'

    @swagger_auto_schema(
        request_body=NinTokenResendSerializer,
        responses=swagger_data.doc_response('nin_verification_token_resend', 'Nin')
    )
    def post(self, request):
        resp = {'status': 404, 'message':'Nin verification not found'}
        serializer = NinTokenResendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nin_v_process = NinVerificationProcess.objects.filter(id=serializer.data['verification_id']).first()
        if nin_v_process:
            _, err_msg = self.make_sms_request(
                self.termii_sms_url, nin_v_process.formated_phone_number, nin_v_process.verification_token
            )
            resp = {'status':400, 'message':err_msg}
            if not err_msg:
                data = {
                    'verification_id':nin_v_process.id, 'msg':'NIN verification token successfully resent'
                }
                resp = {'status':200, 'data':data}
        return response(resp)

class CreateLearnerView(BaseView):
    """
        This endpoint create learner user and profile
    """
    @swagger_auto_schema(
        query_serializer=CreateLearnerQueryParamSerializer,
        request_body=CreateLearnerSerializer,
        responses=swagger_data.doc_response('empty', '')
    )
    def post(self, request):
        q_serializer = CreateLearnerQueryParamSerializer(data=request.query_params)
        q_serializer.is_valid(raise_exception=True)
        verification_id = q_serializer.data['verification_id']
        resp = {'status':400, 'message':'Nin is unverified'}
        if NinVerificationProcess.objects.filter(id=verification_id, nin_is_verified=True).exists():
            resp = {'status':400, 'message':'Unable to create user profile'}
            serializer = CreateLearnerSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            profile = LearnerProfile.create_profile(serializer.data)
            if profile:
                NinVerificationProcess.objects.filter(id=verification_id).update(user=profile.user)
                token, _ = Token.objects.get_or_create(user=profile.user)
                resp = {'status':200, 'data':{'token':token.key}}
        return response(resp)
