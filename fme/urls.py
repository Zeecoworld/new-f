from django.urls import path, include
from fme.views.learner import onbaording
from fme.views.dashboard import administrator, learner, authentication

# dashboard_url = [
#     # authentication
#     path('login', authentication.LoginView.as_view(), name='login'),
#     path('logout', authentication.LogoutView.as_view(), name='logout'),

#     path('change_user_status', administrator.ChangeUserStatusView.as_view(), name='change_user_status'),
#     path('list_learner', learner.ListLearnerView.as_view(), name='list_learner'),
# ]

# documented_urls = [
#     # nin verification and onbaording
#     path('verify_nin', onbaording.VerifyNinView.as_view(), name='verify_nin'),
#     path('create_learner_profile', onbaording.CreateLearnerView.as_view(), name='create_learner_profile'),
#     path('finalize_nin_verification', onbaording.FinalizeNinVerificationView.as_view(), name='finalize_nin_verification'),
#     path('nin_verification_token_resend', onbaording.NinVerificationTokenResendView.as_view(), name='nin_verification_token_resend'),

#     # dashboard
#     path('dashboard/', include(dashboard_url)),
# ]

dashboard_url = [
    # Authentication
    path('login', authentication.LoginView.as_view(), name='login'),
    path('logout', authentication.LogoutView.as_view(), name='logout'),

    # Platform Overview & Analytics
    path('platform_overview', administrator.PlatformOverviewView.as_view(), name='platform_overview'),
    path('scholarship_distribution', administrator.ScholarshipDistributionView.as_view(), name='scholarship_distribution'),
    path('system_health', administrator.SystemHealthView.as_view(), name='system_health'),
    path('advanced_analytics', administrator.AdvancedAnalyticsView.as_view(), name='advanced_analytics'),
    
    # User Management
    path('user_management', administrator.UserManagementView.as_view(), name='user_management'),
    path('change_user_status', administrator.ChangeUserStatusView.as_view(), name='change_user_status'),
    path('bulk_user_action', administrator.BulkUserActionView.as_view(), name='bulk_user_action'),
    path('invite_user', administrator.InviteUserView.as_view(), name='invite_user'),
    
    # Learner Management
    path('list_learner', learner.ListLearnerView.as_view(), name='list_learner'),
    path('learner_analytics', learner.LearnerAnalyticsView.as_view(), name='learner_analytics'),
    path('export_learners', learner.ExportLearnersView.as_view(), name='export_learners'),
    path('learner_bulk_operation', administrator.LearnerBulkOperationView.as_view(), name='learner_bulk_operation'),
    path('learner_detail/<uuid:learner_id>', learner.LearnerDetailView.as_view(), name='learner_detail'),
    
    # Reports & Export
    path('generate_report', administrator.GenerateReportView.as_view(), name='generate_report'),
    path('data_export', administrator.DataExportView.as_view(), name='data_export'),
    
    # System Administration
    path('activity_log', administrator.ActivityLogView.as_view(), name='activity_log'),
    path('send_notification', administrator.NotificationView.as_view(), name='send_notification'),
    path('dashboard_config', administrator.DashboardConfigView.as_view(), name='dashboard_config'),
]

documented_urls = [
    # NIN verification and onboarding
    path('verify_nin', onbaording.VerifyNinView.as_view(), name='verify_nin'),
    path('create_learner_profile', onbaording.CreateLearnerView.as_view(), name='create_learner_profile'),
    path('finalize_nin_verification', onbaording.FinalizeNinVerificationView.as_view(), name='finalize_nin_verification'),
    path('nin_verification_token_resend', onbaording.NinVerificationTokenResendView.as_view(), name='nin_verification_token_resend'),

    # Dashboard
    path('dashboard/', include(dashboard_url)),
]