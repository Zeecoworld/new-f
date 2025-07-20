from django.conf import settings
from rest_framework import views
# from fme.permissions import RestrictedLoginPermission
from rest_framework.permissions import IsAuthenticated #, IsAdminUser
from fme.helpers.request_utils import make_request_for_resp_status, make_request_for_usable_resp

class BaseView(views.APIView):

    def make_nin_request(self, url, nin):
        err_msg = None
        url = f'{url}?nin={nin}'
        options = {'headers':{
            'AppId':settings.DOJAH_NIN_APP_ID,
            'Authorization':settings.DOJAH_NIN_SECRET_KEY
        }}
        resp = make_request_for_usable_resp(url, None, options)
        if not resp or not resp.get('entity'):
            err_msg = 'Unable to verify nin'
            print('*** Something is wrong with nin request: ****', resp)
        return (resp, err_msg)

    def make_sms_request(self, url, phone_number, token):
        err_msg = None
        msg = f"Thanks for taking interest in Digital Training Academy, to proceed use this verification code {token}"
        payload = {
            "to":phone_number,
            "from": settings.TERMII_SMS_SENDER_ID,
            "sms": msg,
            "type": "plain",
            "channel":settings.TERMII_SMS_CHANNEL,
            "api_key": settings.TERMII_SMS_API_KEY
        }
        options = {'method':'post'}
        resp_data, resp_status = make_request_for_resp_status(url, payload, options)
        if resp_status != 200:
            err_msg = "Unable to send sms token"
            print('*** Something is wrong with sms request: ****', resp_data)
        return (resp_data, err_msg)

class BaseAuthenticationView(views.APIView):
    permission_classes = (IsAuthenticated,)
    
class BaseAuthorizationView(views.APIView):
    permission_classes = (IsAuthenticated,)# RestrictedLoginPermission)#, IsAdminUser)

    # def dispatch(self, request, *args, **kwargs):
    #     # First, let DRF handle the basic permission checks
    #     resp = super().dispatch(request, *args, **kwargs)
        
    #     # Additional check after authentication
    #     if request.user.is_authenticated and not RestrictedLoginPermission().has_permission(request, self):
    #        resp = response({'status':403}) 
    #     return resp
