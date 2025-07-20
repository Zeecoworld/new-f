from fme.views.base import BaseAuthorizationView
from fme.serializers.facilitator import FacilitatorInvitationSerializer

class SendFacilitatorInvitationView(BaseAuthorizationView):
    def post(self, request):
        seriailizer = FacilitatorInvitationSerializer(data=request.data)
        if seriailizer.is_valid(raise_exception=True):
            pass