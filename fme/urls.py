from django.urls import path, include
from fme.views.learner import onbaording
from fme.views.dashboard import administrator, learner, authentication

dashboard_url = [
    # authentication
    path('login', authentication.LoginView.as_view(), name='login'),
    path('logout', authentication.LogoutView.as_view(), name='logout'),

    path('change_user_status', administrator.ChangeUserStatusView.as_view(), name='change_user_status'),
    path('list_learner', learner.ListLearnerView.as_view(), name='list_learner'),
]

documented_urls = [
    # nin verification and onbaording
    path('verify_nin', onbaording.VerifyNinView.as_view(), name='verify_nin'),
    path('create_learner_profile', onbaording.CreateLearnerView.as_view(), name='create_learner_profile'),
    path('finalize_nin_verification', onbaording.FinalizeNinVerificationView.as_view(), name='finalize_nin_verification'),
    path('nin_verification_token_resend', onbaording.NinVerificationTokenResendView.as_view(), name='nin_verification_token_resend'),

    # dashboard
    path('dashboard/', include(dashboard_url)),
]
