from response import response
from django.conf import settings
from fme.helpers import swagger_data
from fme.models.learner import LearnerProfile
from drf_yasg.utils import swagger_auto_schema
from fme.views.base import BaseAuthenticationView
from fme.helpers.pagination import PaginationHandlerMixin
from fme.serializers.base import PaginationParamSerializer
from fme.serializers.learner import LearnerProfileSerializer
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from django.http import HttpResponse
import csv
from io import StringIO

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



class LearnerFilterSerializer(serializers.Serializer):
    """Serializer for learner filtering"""
    state = serializers.CharField(max_length=25, required=False)
    account_type = serializers.ChoiceField(
        choices=LearnerProfile.AccountType.choices,
        required=False
    )
    learning_track = serializers.CharField(max_length=100, required=False)
    work_type = serializers.ChoiceField(
        choices=LearnerProfile.WorkType.choices,
        required=False
    )
    gender = serializers.ChoiceField(
        choices=LearnerProfile.Gender.choices,
        required=False
    )
    progress_min = serializers.IntegerField(min_value=0, max_value=100, required=False)
    progress_max = serializers.IntegerField(min_value=0, max_value=100, required=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class ListLearnerView(BaseAuthenticationView, PaginationHandlerMixin):
    """
    Enhanced endpoint to get paginated list of learner profiles with filtering
    """
    
    @swagger_auto_schema(
        query_serializer=PaginationParamSerializer,
        responses=swagger_data.doc_response('list_learner_data', 'LearnerProfile')
    )
    def get(self, request):
        # Parse pagination parameters
        parsed_params = PaginationParamSerializer(data=request.query_params)
        parsed_params.is_valid(raise_exception=True)
        parsed_params = parsed_params.data
        
        # Parse filter parameters
        filter_serializer = LearnerFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data
        
        # Build queryset with filters
        learner_qs = LearnerProfile.objects.select_related('user').all()
        
        if filters.get('state'):
            learner_qs = learner_qs.filter(state=filters['state'])
        
        if filters.get('account_type'):
            learner_qs = learner_qs.filter(account_type=filters['account_type'])
        
        if filters.get('learning_track'):
            learner_qs = learner_qs.filter(learning_track__icontains=filters['learning_track'])
        
        if filters.get('work_type'):
            learner_qs = learner_qs.filter(work_type=filters['work_type'])
        
        if filters.get('gender'):
            learner_qs = learner_qs.filter(gender=filters['gender'])
        
        if filters.get('progress_min') is not None:
            learner_qs = learner_qs.filter(progress__gte=filters['progress_min'])
        
        if filters.get('progress_max') is not None:
            learner_qs = learner_qs.filter(progress__lte=filters['progress_max'])
        
        if filters.get('date_from'):
            learner_qs = learner_qs.filter(created_at__date__gte=filters['date_from'])
        
        if filters.get('date_to'):
            learner_qs = learner_qs.filter(created_at__date__lte=filters['date_to'])
        
        # Apply pagination
        self.page_size = parsed_params.get('page_size', settings.DEFAULT_PAGINATION_SIZE)
        paginate_qs = self.paginate_queryset(learner_qs, request, view=self)
        learner_serializer = LearnerProfileSerializer(paginate_qs, many=True).data
        
        if learner_serializer is not None:  # Check for None instead of truthy check
            return response({
                "status": 200, 
                "data": self.get_paginated_response(learner_serializer)
            })
        
        return response({"status": 400, "message": "Record not found"})


class LearnerAnalyticsView(BaseAuthenticationView):
    """
    Comprehensive learner analytics for dashboard
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'LearnerAnalytics')
    )
    def get(self, request):
        now = timezone.now()
        
        # Basic counts
        total_learners = LearnerProfile.objects.count()
        active_learners = LearnerProfile.objects.filter(
            user__last_active__gte=now - timedelta(days=30)
        ).count()
        
        # Progress analytics
        progress_distribution = {
            'beginner': LearnerProfile.objects.filter(progress__lt=25).count(),
            'intermediate': LearnerProfile.objects.filter(
                progress__gte=25, progress__lt=75
            ).count(),
            'advanced': LearnerProfile.objects.filter(progress__gte=75).count(),
            'completed': LearnerProfile.objects.filter(progress=100).count(),
        }
        
        # Demographics
        gender_distribution = LearnerProfile.objects.values('gender').annotate(
            count=Count('id')
        )
        
        state_distribution = LearnerProfile.objects.values('state').annotate(
            count=Count('id')
        ).order_by('-count')[:10]  # Top 10 states
        
        # Learning tracks
        track_distribution = LearnerProfile.objects.values('learning_track').annotate(
            count=Count('id'),
            avg_progress=Avg('progress')
        ).order_by('-count')
        
        # Work type preferences
        work_type_distribution = LearnerProfile.objects.values('work_type').annotate(
            count=Count('id')
        )
        
        # Account type distribution
        account_type_distribution = LearnerProfile.objects.values('account_type').annotate(
            count=Count('id')
        )
        
        # Monthly registration trend (last 12 months)
        monthly_registrations = []
        for i in range(12):
            month_start = now - timedelta(days=30 * (i + 1))
            month_end = now - timedelta(days=30 * i)
            count = LearnerProfile.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            monthly_registrations.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        # Performance metrics
        avg_progress = LearnerProfile.objects.aggregate(
            avg=Avg('progress')
        )['avg'] or 0
        
        completion_rate = (progress_distribution['completed'] / max(total_learners, 1)) * 100
        
        data = {
            'summary': {
                'total_learners': total_learners,
                'active_learners': active_learners,
                'completion_rate': round(completion_rate, 1),
                'avg_progress': round(avg_progress, 1)
            },
            'progress_distribution': progress_distribution,
            'demographics': {
                'gender': list(gender_distribution),
                'states': list(state_distribution),
                'account_types': list(account_type_distribution),
                'work_types': list(work_type_distribution)
            },
            'learning_tracks': list(track_distribution),
            'trends': {
                'monthly_registrations': monthly_registrations[::-1]  # Reverse for chronological order
            }
        }
        
        return response({'status': 200, 'data': data})


class ExportLearnersView(BaseAuthenticationView):
    """
    Export learners data to CSV
    """
    
    def get(self, request):
        # Parse filter parameters (reuse the same filter logic)
        filter_serializer = LearnerFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data
        
        # Build queryset with filters (same logic as ListLearnerView)
        learner_qs = LearnerProfile.objects.select_related('user').all()
        
        # Apply the same filters as in ListLearnerView
        if filters.get('state'):
            learner_qs = learner_qs.filter(state=filters['state'])
        if filters.get('account_type'):
            learner_qs = learner_qs.filter(account_type=filters['account_type'])
        if filters.get('learning_track'):
            learner_qs = learner_qs.filter(learning_track__icontains=filters['learning_track'])
        if filters.get('work_type'):
            learner_qs = learner_qs.filter(work_type=filters['work_type'])
        if filters.get('gender'):
            learner_qs = learner_qs.filter(gender=filters['gender'])
        if filters.get('progress_min') is not None:
            learner_qs = learner_qs.filter(progress__gte=filters['progress_min'])
        if filters.get('progress_max') is not None:
            learner_qs = learner_qs.filter(progress__lte=filters['progress_max'])
        if filters.get('date_from'):
            learner_qs = learner_qs.filter(created_at__date__gte=filters['date_from'])
        if filters.get('date_to'):
            learner_qs = learner_qs.filter(created_at__date__lte=filters['date_to'])
        
        # Create CSV response
        response_obj = HttpResponse(content_type='text/csv')
        response_obj['Content-Disposition'] = 'attachment; filename="learners_export.csv"'
        
        writer = csv.writer(response_obj)
        
        # Write header
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'Email', 'Phone', 'State',
            'Gender', 'Account Type', 'Learning Track', 'Skill Cluster',
            'Work Type', 'Industrial Preference', 'Progress (%)', 
            'Registration Date', 'Last Active', 'Status'
        ])
        
        # Write data rows
        for learner in learner_qs:
            writer.writerow([
                str(learner.user.id),
                learner.user.first_name,
                learner.user.last_name,
                learner.user.email,
                learner.user.phone_number,
                learner.get_state_display(),
                learner.get_gender_display(),
                learner.get_account_type_display(),
                learner.learning_track,
                learner.skill_cluster,
                learner.get_work_type_display(),
                learner.industrial_prefrence,
                learner.progress,
                learner.created_at.strftime('%Y-%m-%d'),
                learner.user.last_active.strftime('%Y-%m-%d %H:%M') if learner.user.last_active else '',
                learner.user.get_status_display()
            ])
        
        return response_obj


class LearnerDetailView(BaseAuthenticationView):
    """
    Get detailed information about a specific learner
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'LearnerDetail')
    )
    def get(self, request, learner_id):
        try:
            learner = LearnerProfile.objects.select_related('user').get(
                user__id=learner_id
            )
            
            serializer = LearnerProfileSerializer(learner)
            
            # Add additional analytics for this specific learner
            data = serializer.data
            data['analytics'] = {
                'days_since_registration': (timezone.now() - learner.created_at).days,
                'last_activity_days_ago': (
                    timezone.now() - learner.user.last_active
                ).days if learner.user.last_active else None,
                'is_active_learner': learner.user.last_active and 
                    learner.user.last_active >= timezone.now() - timedelta(days=7)
            }
            
            return response({'status': 200, 'data': data})
            
        except LearnerProfile.DoesNotExist:
            return response({'status': 404, 'message': 'Learner not found'})