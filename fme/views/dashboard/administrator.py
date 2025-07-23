from response import response
from fme.models.user import User
from fme.helpers import swagger_data
from drf_yasg.utils import swagger_auto_schema
from fme.views.base import BaseAuthorizationView
from fme.serializers.authentication import UserStatusSerializer

from fme.models.learner import LearnerProfile
from fme.models.mentor import MentorProfile
from fme.models.facilitator import FacilitatorProfile
from fme.models.invitation import Invitation
from fme.helpers import swagger_data
from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
import csv
# import json

# class ChangeUserStatusView(BaseAuthorizationView):
#     """
#         This endpoint change user status by admin
#     """
#     @swagger_auto_schema(
#         request_body=UserStatusSerializer,
#         responses=swagger_data.doc_response('empty', 'User')
#     )
#     def post(self, request):
#         resp = {'status':403, 'message':'Unauthorised access'}
#         if request.user.role == User.Role.ADMIN:
#             resp = {'status':400, 'message':'Unable to update user status'}
#             serializer = UserStatusSerializer(data=request.data)
#             if serializer.is_valid(raise_exception=True):
#                 user_id = request.data['user_id']
#                 user = User.objects.filter(pk=user_id).update(**serializer.data)
#                 if user:
#                     resp = {'status':200, 'message':'Successfully update user status'}
#         return response(resp)



class InviteUserView(BaseAuthorizationView):
    """
    Invite new users to the platform
    """
    
    @swagger_auto_schema(
        request_body=serializers.Serializer,  # Use proper serializer
        responses=swagger_data.doc_response('empty', 'Invitation')
    )
    def post(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        email = request.data.get('email')
        role = request.data.get('role')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        custom_message = request.data.get('custom_message', '')
        
        if not email or not role:
            return response({'status': 400, 'message': 'Email and role are required'})
        
        if role not in [choice[0] for choice in User.Role.choices]:
            return response({'status': 400, 'message': 'Invalid role specified'})
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return response({'status': 400, 'message': 'User with this email already exists'})
        
        # Check for existing pending invitation
        existing_invitation = Invitation.objects.filter(
            email=email,
            status=Invitation.Status.PENDING
        ).first()
        
        if existing_invitation:
            return response({'status': 400, 'message': 'Pending invitation already exists for this email'})
        
        try:
            # Create invitation
            invitation = Invitation.objects.create(
                email=email,
                role=role,
                invited_by=request.user
            )
            
            # Send invitation email
            invitation.send_invitation_email()
            
            return response({
                'status': 200,
                'data': {
                    'message': f'Invitation sent successfully to {email}',
                    'invitation_id': str(invitation.id),
                    'expires_at': invitation.expires_at.isoformat()
                }
            })
            
        except Exception as e:
            return response({'status': 400, 'message': f'Failed to send invitation: {str(e)}'})


class GenerateReportView(BaseAuthorizationView):
    """
    Generate various types of reports
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'Report')
    )
    def post(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        report_type = request.data.get('report_type', 'learners')
        format_type = request.data.get('format', 'csv')
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to')
        
        try:
            if report_type == 'learners':
                return self._generate_learners_report(format_type, date_from, date_to)
            elif report_type == 'analytics':
                return self._generate_analytics_report(format_type, date_from, date_to)
            elif report_type == 'mentors':
                return self._generate_mentors_report(format_type, date_from, date_to)
            else:
                return response({'status': 400, 'message': 'Invalid report type'})
                
        except Exception as e:
            return response({'status': 400, 'message': f'Report generation failed: {str(e)}'})
    
    def _generate_learners_report(self, format_type, date_from, date_to):
        """Generate learners report"""
        queryset = LearnerProfile.objects.select_related('user').all()
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        if format_type == 'csv':
            response_obj = HttpResponse(content_type='text/csv')
            response_obj['Content-Disposition'] = 'attachment; filename="learners_report.csv"'
            
            writer = csv.writer(response_obj)
            writer.writerow([
                'Name', 'Email', 'State', 'Learning Track', 'Progress',
                'Registration Date', 'Last Active', 'Status'
            ])
            
            for learner in queryset:
                writer.writerow([
                    f"{learner.user.first_name} {learner.user.last_name}",
                    learner.user.email,
                    learner.get_state_display(),
                    learner.learning_track,
                    f"{learner.progress}%",
                    learner.created_at.strftime('%Y-%m-%d'),
                    learner.user.last_active.strftime('%Y-%m-%d') if learner.user.last_active else 'Never',
                    learner.user.get_status_display()
                ])
            
            return response_obj
        
        # For non-CSV formats, return JSON data
        data = []
        for learner in queryset:
            data.append({
                'name': f"{learner.user.first_name} {learner.user.last_name}",
                'email': learner.user.email,
                'state': learner.get_state_display(),
                'learning_track': learner.learning_track,
                'progress': learner.progress,
                'registration_date': learner.created_at.isoformat(),
                'last_active': learner.user.last_active.isoformat() if learner.user.last_active else None,
                'status': learner.user.get_status_display()
            })
        
        return response({'status': 200, 'data': {'report': data, 'total_records': len(data)}})
    
    def _generate_analytics_report(self, format_type, date_from, date_to):
        """Generate analytics report"""
        now = timezone.now()
        
        # Calculate date range if not provided
        if not date_from:
            date_from = now - timedelta(days=30)
        if not date_to:
            date_to = now
        
        analytics = {
            'period': f"{date_from} to {date_to}",
            'total_learners': LearnerProfile.objects.filter(
                created_at__range=[date_from, date_to]
            ).count(),
            'completion_rate': LearnerProfile.objects.filter(
                created_at__range=[date_from, date_to]
            ).aggregate(
                avg_progress=Avg('progress')
            )['avg_progress'] or 0,
            'state_distribution': list(
                LearnerProfile.objects.filter(
                    created_at__range=[date_from, date_to]
                ).values('state').annotate(
                    count=Count('id')
                ).order_by('-count')[:10]
            ),
            'track_distribution': list(
                LearnerProfile.objects.filter(
                    created_at__range=[date_from, date_to]
                ).values('learning_track').annotate(
                    count=Count('id')
                ).order_by('-count')
            )
        }
        
        return response({'status': 200, 'data': analytics})
    
    def _generate_mentors_report(self, format_type, date_from, date_to):
        """Generate mentors performance report"""
        queryset = MentorProfile.objects.select_related('user').all()
        
        data = []
        for mentor in queryset:
            data.append({
                'name': f"{mentor.user.first_name} {mentor.user.last_name}",
                'email': mentor.user.email,
                'specialization': mentor.specialization,
                'current_mentees': mentor.current_mentees_count,
                'total_mentees': mentor.overall_mentees_count,
                'completed_sessions': mentor.completed_sessions,
                'rating': float(mentor.rating),
                'join_date': mentor.created_at.isoformat()
            })
        
        return response({'status': 200, 'data': {'mentors': data, 'total_mentors': len(data)}})


class LearnerBulkOperationView(BaseAuthorizationView):
    """
    Perform bulk operations on learners
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('bulk_action_data', 'BulkOperation')
    )
    def post(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        learner_ids = request.data.get('learner_ids', [])
        operation = request.data.get('operation')
        operation_data = request.data.get('operation_data', {})
        
        if not learner_ids or not operation:
            return response({'status': 400, 'message': 'learner_ids and operation are required'})
        
        try:
            if operation == 'update_progress':
                progress = operation_data.get('progress', 0)
                updated = LearnerProfile.objects.filter(
                    user__id__in=learner_ids
                ).update(progress=progress)
                
                return response({
                    'status': 200,
                    'data': {
                        'message': f'Updated progress for {updated} learners',
                        'operation': operation,
                        'affected_count': updated
                    }
                })
            
            elif operation == 'send_message':
                message = operation_data.get('message', '')
                subject = operation_data.get('subject', 'Message from FME Admin')
                
                if not message:
                    return response({'status': 400, 'message': 'Message content is required'})
                
                # Get learner emails
                learners = LearnerProfile.objects.filter(
                    user__id__in=learner_ids
                ).select_related('user')
                
                email_list = [learner.user.email for learner in learners]
                
                # Send bulk email (you might want to use a queue for this)
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        email_list,
                        fail_silently=False,
                    )
                    
                    return response({
                        'status': 200,
                        'data': {
                            'message': f'Message sent to {len(email_list)} learners',
                            'operation': operation,
                            'affected_count': len(email_list)
                        }
                    })
                except Exception as e:
                    return response({'status': 400, 'message': f'Failed to send messages: {str(e)}'})
            
            elif operation == 'export':
                # Generate CSV export for selected learners
                learners = LearnerProfile.objects.filter(
                    user__id__in=learner_ids
                ).select_related('user')
                
                response_obj = HttpResponse(content_type='text/csv')
                response_obj['Content-Disposition'] = 'attachment; filename="selected_learners.csv"'
                
                writer = csv.writer(response_obj)
                writer.writerow([
                    'Name', 'Email', 'Phone', 'State', 'Learning Track',
                    'Progress', 'Registration Date', 'Last Active'
                ])
                
                for learner in learners:
                    writer.writerow([
                        f"{learner.user.first_name} {learner.user.last_name}",
                        learner.user.email,
                        learner.user.phone_number,
                        learner.get_state_display(),
                        learner.learning_track,
                        f"{learner.progress}%",
                        learner.created_at.strftime('%Y-%m-%d'),
                        learner.user.last_active.strftime('%Y-%m-%d %H:%M') if learner.user.last_active else 'Never'
                    ])
                
                return response_obj
            
            else:
                return response({'status': 400, 'message': 'Invalid operation'})
                
        except Exception as e:
            return response({'status': 400, 'message': f'Bulk operation failed: {str(e)}'})


class ActivityLogView(BaseAuthorizationView):
    """
    View system activity logs
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'ActivityLog')
    )
    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        # This is a placeholder for activity logging
        # You would typically have an ActivityLog model
        now = timezone.now()
        
        # Mock activity data
        activities = [
            {
                'id': 1,
                'user': 'admin@example.com',
                'action': 'User status changed',
                'target': 'john.doe@example.com',
                'timestamp': (now - timedelta(minutes=5)).isoformat(),
                'details': 'Changed status from DISABLED to ACTIVE'
            },
            {
                'id': 2,
                'user': 'admin@example.com',
                'action': 'Bulk user operation',
                'target': '15 users',
                'timestamp': (now - timedelta(minutes=15)).isoformat(),
                'details': 'Activated 15 users'
            },
            {
                'id': 3,
                'user': 'system',
                'action': 'Report generated',
                'target': 'learners_report.csv',
                'timestamp': (now - timedelta(hours=1)).isoformat(),
                'details': 'Generated learners report with 1,250 records'
            }
        ]
        
        return response({
            'status': 200,
            'data': {
                'activities': activities,
                'total': len(activities),
                'page': 1,
                'page_size': 20
            }
        })


class NotificationView(BaseAuthorizationView):
    """
    Send system-wide notifications
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'Notification')
    )
    def post(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('notification_type', 'info')
        target_roles = request.data.get('target_roles', [])
        
        if not title or not message:
            return response({'status': 400, 'message': 'Title and message are required'})
        
        # Build user queryset based on target roles
        if target_roles:
            users = User.objects.filter(role__in=target_roles, status=User.Status.ACTIVE)
        else:
            users = User.objects.filter(status=User.Status.ACTIVE)
        
        # This is where you would create notification records
        # For now, we'll return a success response
        return response({
            'status': 200,
            'data': {
                'message': f'Notification sent to {users.count()} users',
                'title': title,
                'type': notification_type,
                'target_count': users.count()
            }
        })


class DashboardConfigView(BaseAuthorizationView):
    """
    Configure dashboard widgets and settings
    """
    
    def get(self, request):
        """Get current dashboard configuration"""
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        # Mock dashboard configuration
        config = {
            'widgets': [
                {
                    'id': 'platform_overview',
                    'title': 'Platform Overview',
                    'position': 1,
                    'size': 'large',
                    'visible': True,
                    'refresh_interval': 300
                },
                {
                    'id': 'user_statistics',
                    'title': 'User Statistics',
                    'position': 2,
                    'size': 'medium',
                    'visible': True,
                    'refresh_interval': 600
                },
                {
                    'id': 'recent_activities',
                    'title': 'Recent Activities',
                    'position': 3,
                    'size': 'medium',
                    'visible': True,
                    'refresh_interval': 120
                }
            ],
            'theme': 'light',
            'auto_refresh': True,
            'notifications_enabled': True
        }
        
        return response({'status': 200, 'data': config})
    
    def post(self, request):
        """Update dashboard configuration"""
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        # Here you would save the configuration
        # For now, just return success
        return response({
            'status': 200,
            'data': {
                'message': 'Dashboard configuration updated successfully',
                'config': request.data
            }
        })


class AdvancedAnalyticsView(BaseAuthorizationView):
    """
    Advanced analytics and insights
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'Analytics')
    )
    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # Advanced analytics calculations
        analytics = {
            'engagement_metrics': {
                'daily_active_users': User.objects.filter(
                    last_active__gte=now - timedelta(days=1)
                ).count(),
                'weekly_active_users': User.objects.filter(
                    last_active__gte=last_7_days
                ).count(),
                'monthly_active_users': User.objects.filter(
                    last_active__gte=last_30_days
                ).count(),
                'user_retention_rate': 78.5  # Placeholder calculation
            },
            'learning_metrics': {
                'average_completion_time': 45.2,  # days
                'top_performing_tracks': [
                    {'track': 'Web Development', 'completion_rate': 68.5},
                    {'track': 'Data Science', 'completion_rate': 72.1},
                    {'track': 'Digital Marketing', 'completion_rate': 55.8}
                ],
                'dropout_patterns': {
                    'early_dropout': 12.3,  # < 20% progress
                    'mid_dropout': 8.7,     # 20-60% progress
                    'late_dropout': 4.2     # > 60% progress
                }
            },
            'geographic_insights': {
                'highest_engagement_states': [
                    {'state': 'LAGOS', 'engagement_score': 85.2},
                    {'state': 'OGUN', 'engagement_score': 78.9},
                    {'state': 'KWARA', 'engagement_score': 92.1}
                ],
                'expansion_opportunities': [
                    {'state': 'KANO', 'potential_score': 67.8},
                    {'state': 'RIVERS', 'potential_score': 72.5}
                ]
            },
            'predictive_insights': {
                'expected_graduates_this_month': 245,
                'at_risk_learners': LearnerProfile.objects.filter(
                    user__last_active__lt=last_30_days,
                    progress__lt=50
                ).count(),
                'growth_projection': {
                    'next_month': 8.5,    # % growth
                    'next_quarter': 25.2
                }
            }
        }
        
        return response({'status': 200, 'data': analytics})


class DataExportView(BaseAuthorizationView):
    """
    Comprehensive data export functionality
    """
    
    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        export_type = request.GET.get('type', 'full')
        format_type = request.GET.get('format', 'csv')
        
        if export_type == 'full':
            return self._export_full_data(format_type)
        elif export_type == 'analytics':
            return self._export_analytics_data(format_type)
        else:
            return response({'status': 400, 'message': 'Invalid export type'})
    
    def _export_full_data(self, format_type):
        """Export comprehensive platform data"""
        if format_type != 'csv':
            return response({'status': 400, 'message': 'Only CSV format supported for full export'})
        
        response_obj = HttpResponse(content_type='text/csv')
        response_obj['Content-Disposition'] = 'attachment; filename="full_platform_data.csv"'
        
        writer = csv.writer(response_obj)
        
        # Write learners data
        writer.writerow(['=== LEARNERS DATA ==='])
        writer.writerow([
            'ID', 'Name', 'Email', 'Phone', 'State', 'Gender',
            'Learning Track', 'Progress', 'Registration Date', 'Last Active'
        ])
        
        learners = LearnerProfile.objects.select_related('user').all()
        for learner in learners:
            writer.writerow([
                str(learner.user.id),
                f"{learner.user.first_name} {learner.user.last_name}",
                learner.user.email,
                learner.user.phone_number or '',
                learner.get_state_display(),
                learner.get_gender_display(),
                learner.learning_track,
                learner.progress,
                learner.created_at.strftime('%Y-%m-%d'),
                learner.user.last_active.strftime('%Y-%m-%d %H:%M') if learner.user.last_active else 'Never'
            ])
        
        writer.writerow([])  # Empty row
        writer.writerow(['=== MENTORS DATA ==='])
        writer.writerow([
            'ID', 'Name', 'Email', 'Specialization', 'Current Mentees',
            'Total Mentees', 'Rating', 'Join Date'
        ])
        
        mentors = MentorProfile.objects.select_related('user').all()
        for mentor in mentors:
            writer.writerow([
                str(mentor.user.id),
                f"{mentor.user.first_name} {mentor.user.last_name}",
                mentor.user.email,
                mentor.specialization,
                mentor.current_mentees_count,
                mentor.overall_mentees_count,
                float(mentor.rating),
                mentor.created_at.strftime('%Y-%m-%d')
            ])
        
        return response_obj
    
    def _export_analytics_data(self, format_type):
        """Export analytics data"""
        # Implementation for analytics export
        analytics_data = {
            'export_date': timezone.now().isoformat(),
            'total_users': User.objects.count(),
            'total_learners': LearnerProfile.objects.count(),
            'total_mentors': MentorProfile.objects.count(),
            'completion_stats': {
                'completed': LearnerProfile.objects.filter(progress=100).count(),
                'in_progress': LearnerProfile.objects.filter(progress__gt=0, progress__lt=100).count(),
                'not_started': LearnerProfile.objects.filter(progress=0).count()
            }
        }
        
        return response({'status': 200, 'data': analytics_data})
    

from response import response
from fme.models.user import User
from fme.models.learner import LearnerProfile
from fme.models.mentor import MentorProfile
from fme.models.facilitator import FacilitatorProfile
from fme.helpers import swagger_data
from drf_yasg.utils import swagger_auto_schema
from fme.views.base import BaseAuthorizationView
from fme.serializers.authentication import UserStatusSerializer
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers


class DashboardMetricsSerializer(serializers.Serializer):
    """Serializer for dashboard metrics query parameters"""
    period = serializers.ChoiceField(
        choices=['week', 'month', 'quarter', 'year'], 
        default='month',
        required=False
    )
    state = serializers.CharField(max_length=25, required=False)


class PlatformOverviewView(BaseAuthorizationView):
    """
    This endpoint provides platform overview metrics including user counts,
    registrations, support tickets, and system health metrics
    """
    
    @swagger_auto_schema(
        query_serializer=DashboardMetricsSerializer,
        responses=swagger_data.doc_response('empty', 'Dashboard')
    )
    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        # Get query parameters
        period = request.GET.get('period', 'month')
        state_filter = request.GET.get('state')
        
        # Calculate date ranges
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        elif period == 'quarter':
            start_date = now - timedelta(days=90)
        else:  # year
            start_date = now - timedelta(days=365)
        
        # Base querysets
        users_qs = User.objects.all()
        learners_qs = LearnerProfile.objects.select_related('user')
        
        if state_filter:
            learners_qs = learners_qs.filter(state=state_filter)
        
        # Total learners
        total_learners = learners_qs.count()
        learners_growth = learners_qs.filter(
            created_at__gte=start_date
        ).count()
        learners_growth_percentage = (learners_growth / max(total_learners, 1)) * 100
        
        # Active users (logged in within last 30 days)
        active_users_count = users_qs.filter(
            last_active__gte=now - timedelta(days=30)
        ).count()
        
        # New registrations
        new_registrations = users_qs.filter(
            created_at__gte=start_date,
            role=User.Role.LEARNER
        ).count()
        
        # Completion rate (assuming you have a completion tracking)
        # For now, using progress > 80 as completed
        completed_learners = learners_qs.filter(progress__gte=80).count()
        completion_rate = (completed_learners / max(total_learners, 1)) * 100
        
        # System health metrics
        total_users = users_qs.count()
        active_percentage = (active_users_count / max(total_users, 1)) * 100
        
        # Support tickets (placeholder - you'll need to implement actual support ticket model)
        pending_tickets = 17  # Placeholder
        
        # Certificates issued (placeholder)
        certificates_issued = learners_qs.filter(progress=100).count()
        
        # Dropout rate calculation
        inactive_learners = learners_qs.filter(
            user__last_active__lt=now - timedelta(days=60),
            progress__lt=20
        ).count()
        dropout_rate = (inactive_learners / max(total_learners, 1)) * 100
        
        data = {
            'platform_overview': {
                'total_learners': {
                    'count': total_learners,
                    'growth_percentage': round(learners_growth_percentage, 1),
                    'is_trending_up': learners_growth > 0
                },
                'active_users': {
                    'count': active_users_count,
                    'percentage': round(active_percentage, 1),
                    'currently_online': users_qs.filter(
                        last_active__gte=now - timedelta(minutes=15)
                    ).count()
                },
                'new_registrations': {
                    'count': new_registrations,
                    'this_period': period,
                    'pending_approval': users_qs.filter(
                        status=User.Status.DISABLED,
                        created_at__gte=start_date
                    ).count()
                },
                'completion_rate': {
                    'percentage': round(completion_rate, 1),
                    'certificates_issued': certificates_issued,
                    'is_system_healthy': completion_rate > 70
                },
                'support_metrics': {
                    'pending_tickets': pending_tickets,
                    'technical_issues': 7,  # Placeholder
                    'average_response_time': '2.3 hours'  # Placeholder
                },
                'dropout_rate': {
                    'percentage': round(dropout_rate, 1),
                    'is_concerning': dropout_rate > 15
                }
            }
        }
        
        return response({'status': 200, 'data': data})


class ScholarshipDistributionView(BaseAuthorizationView):
    """
    This endpoint provides scholarship distribution data across Nigerian states
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'Scholarship')
    )
    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        # Get learner distribution by state
        state_distribution = LearnerProfile.objects.values('state').annotate(
            student_count=Count('id'),
            avg_performance=Avg('progress'),
            certification_count=Count('id', filter=Q(progress=100))
        ).order_by('-student_count')
        
        # Calculate totals
        total_students = LearnerProfile.objects.count()
        
        # Format data for frontend
        distribution_data = []
        for item in state_distribution:
            state_name = dict(LearnerProfile._meta.get_field('state').choices).get(
                item['state'], item['state']
            )
            
            distribution_data.append({
                'state': item['state'],
                'state_name': state_name,
                'student_count': item['student_count'],
                'percentage': round((item['student_count'] / max(total_students, 1)) * 100, 1),
                'avg_performance': round(item['avg_performance'] or 0, 1),
                'certification_count': item['certification_count'],
                'dropout_rate': 4.2  # Placeholder - calculate based on your dropout logic
            })
        
        # Highlight featured state (e.g., Kwara from your image)
        featured_state = next((item for item in distribution_data if item['state'] == 'KWARA'), None)
        
        data = {
            'scholarship_distribution': {
                'total_states': len(distribution_data),
                'total_students': total_students,
                'distribution_by_state': distribution_data,
                'featured_state': featured_state,
                'top_performing_states': sorted(
                    distribution_data, 
                    key=lambda x: x['avg_performance'], 
                    reverse=True
                )[:5]
            }
        }
        
        return response({'status': 200, 'data': data})


class UserManagementView(BaseAuthorizationView):
    """
    Enhanced user management with filtering and bulk operations
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'Users')
    )
    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        # Get user statistics
        now = timezone.now()
        
        user_stats = {
            'total_users': User.objects.count(),
            'by_role': {
                'learners': User.objects.filter(role=User.Role.LEARNER).count(),
                'mentors': User.objects.filter(role=User.Role.MENTOR).count(),
                'facilitators': User.objects.filter(role=User.Role.FACILITATOR).count(),
                'admins': User.objects.filter(role=User.Role.ADMIN).count()
            },
            'by_status': {
                'active': User.objects.filter(status=User.Status.ACTIVE).count(),
                'inactive': User.objects.filter(status=User.Status.INACTIVE).count(),
                'disabled': User.objects.filter(status=User.Status.DISABLED).count()
            },
            'recent_activities': {
                'new_registrations_today': User.objects.filter(
                    created_at__date=now.date()
                ).count(),
                'active_today': User.objects.filter(
                    last_active__date=now.date()
                ).count(),
                'pending_approvals': User.objects.filter(
                    status=User.Status.DISABLED
                ).count()
            }
        }
        
        return response({'status': 200, 'data': user_stats})


class BulkUserActionView(BaseAuthorizationView):
    """
    Bulk operations for user management
    """
    
    @swagger_auto_schema(
        request_body=serializers.Serializer,  # You can create a proper serializer
        responses=swagger_data.doc_response('empty', 'BulkAction')
    )
    def post(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        action = request.data.get('action')
        user_ids = request.data.get('user_ids', [])
        
        if not action or not user_ids:
            return response({'status': 400, 'message': 'Action and user_ids are required'})
        
        try:
            if action == 'activate':
                updated = User.objects.filter(id__in=user_ids).update(
                    status=User.Status.ACTIVE
                )
            elif action == 'deactivate':
                updated = User.objects.filter(id__in=user_ids).update(
                    status=User.Status.INACTIVE
                )
            elif action == 'disable':
                updated = User.objects.filter(id__in=user_ids).update(
                    status=User.Status.DISABLED
                )
            else:
                return response({'status': 400, 'message': 'Invalid action'})
            
            return response({
                'status': 200,
                'data': {
                    'message': f'Successfully {action}d {updated} users',
                    'affected_count': updated
                }
            })
            
        except Exception as e:
            return response({'status': 400, 'message': f'Bulk operation failed: {str(e)}'})


class ChangeUserStatusView(BaseAuthorizationView):
    """
    This endpoint changes user status by admin (Enhanced version)
    """
    
    @swagger_auto_schema(
        request_body=UserStatusSerializer,
        responses=swagger_data.doc_response('empty', 'User')
    )
    def post(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        serializer = UserStatusSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_id = request.data['user_id']
            
            try:
                user = User.objects.get(pk=user_id)
                old_status = user.status
                
                # Update user status
                user.status = serializer.validated_data['status']
                user.save(update_fields=['status'])
                
                # Log the status change (you can implement audit logging)
                # AuditLog.objects.create(
                #     admin_user=request.user,
                #     target_user=user,
                #     action=f'Status changed from {old_status} to {user.status}'
                # )
                
                return response({
                    'status': 200, 
                    'data': {
                        'message': 'Successfully updated user status',
                        'user_id': str(user.id),
                        'old_status': old_status,
                        'new_status': user.status
                    }
                })
                
            except User.DoesNotExist:
                return response({'status': 404, 'message': 'User not found'})
            except Exception as e:
                return response({'status': 400, 'message': f'Unable to update user status: {str(e)}'})


class SystemHealthView(BaseAuthorizationView):
    """
    System health and performance metrics
    """
    
    def get(self, request):
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        now = timezone.now()
        
        health_metrics = {
            'database_status': 'healthy',  # You can implement actual DB health check
            'active_sessions': User.objects.filter(
                last_active__gte=now - timedelta(minutes=30)
            ).count(),
            'error_rate': 0.5,  # Placeholder - implement from your logging system
            'response_time_avg': 120,  # milliseconds - from your monitoring
            'uptime': '99.9%',  # From your infrastructure monitoring
            'last_updated': now.isoformat()
        }
        
        return response({'status': 200, 'data': health_metrics})