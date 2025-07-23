from response import response
from django.conf import settings
from django.db.models import Q, Count, Avg, F,Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from fme.helpers import swagger_data
from fme.helpers.pagination import PaginationHandlerMixin
from fme.views.base import BaseAuthorizationView
from fme.models.skill_area import (
    SkillArea, SkillAreaModule, LearnerSkillAreaProgress,
    LearnerModuleProgress, SkillAreaAssessment
)
from fme.models.user import User
from fme.serializers.skill_area import (
    SkillAreaListSerializer, SkillAreaDetailSerializer,
    SkillAreaCreateUpdateSerializer, SkillAreaModuleSerializer,
    LearnerSkillAreaProgressSerializer, LearnerModuleProgressSerializer,
    SkillAreaAssessmentSerializer, SkillAreaFilterSerializer,
    SkillAreaStatsSerializer, BulkSkillAreaActionSerializer
)
from fme.serializers.base import PaginationParamSerializer


class SkillAreaViewSet(ModelViewSet, BaseAuthorizationView, PaginationHandlerMixin):
    """
    ViewSet for managing skill areas
    Supports CRUD operations, filtering, and analytics
    """
    queryset = SkillArea.objects.all().prefetch_related('modules', 'created_by')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SkillAreaListSerializer
        elif self.action == 'retrieve':
            return SkillAreaDetailSerializer
        else:
            return SkillAreaCreateUpdateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        target_audience = self.request.query_params.get('target_audience')
        search = self.request.query_params.get('search')
        created_by = self.request.query_params.get('created_by')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if target_audience:
            queryset = queryset.filter(target_audience=target_audience)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(learning_objectives__icontains=search)
            )
        
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        
        # Completion rate filters
        min_rate = self.request.query_params.get('min_completion_rate')
        max_rate = self.request.query_params.get('max_completion_rate')
        
        if min_rate:
            queryset = queryset.filter(avg_completion_rate__gte=min_rate)
        if max_rate:
            queryset = queryset.filter(avg_completion_rate__lte=max_rate)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    @swagger_auto_schema(
        query_serializer=SkillAreaFilterSerializer,
        responses=swagger_data.doc_response('empty', 'SkillArea')
    )
    def list(self, request):
        """List all skill areas with filtering and pagination"""
        queryset = self.get_queryset()
        
        # Apply pagination
        page_size = request.query_params.get('page_size', settings.DEFAULT_PAGINATION_SIZE)
        self.page_size = int(page_size)
        
        paginated_queryset = self.paginate_queryset(queryset, request, view=self)
        serializer = self.get_serializer(paginated_queryset, many=True)
        
        paginated_response = self.get_paginated_response(serializer.data)
        return response({'status': 200, 'data': paginated_response})
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'SkillArea')
    )
    def retrieve(self, request, pk=None):
        """Get detailed information about a specific skill area"""
        try:
            skill_area = self.get_object()
            serializer = self.get_serializer(skill_area)
            return response({'status': 200, 'data': serializer.data})
        except SkillArea.DoesNotExist:
            return response({'status': 404, 'message': 'Skill area not found'})
    
    @swagger_auto_schema(
        request_body=SkillAreaCreateUpdateSerializer,
        responses=swagger_data.doc_response('empty', 'SkillArea')
    )
    def create(self, request):
        """Create a new skill area"""
        if request.user.role not in [User.Role.ADMIN, User.Role.FACILITATOR]:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            skill_area = serializer.save()
            return response({
                'status': 201,
                'data': SkillAreaDetailSerializer(skill_area).data,
                'message': 'Skill area created successfully'
            })
        return response({'status': 400, 'message': 'Validation error', 'errors': serializer.errors})
    
    @swagger_auto_schema(
        request_body=SkillAreaCreateUpdateSerializer,
        responses=swagger_data.doc_response('empty', 'SkillArea')
    )
    def update(self, request, pk=None):
        """Update a skill area"""
        if request.user.role not in [User.Role.ADMIN, User.Role.FACILITATOR]:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        try:
            skill_area = self.get_object()
            serializer = self.get_serializer(skill_area, data=request.data, partial=True)
            if serializer.is_valid():
                skill_area = serializer.save()
                return response({
                    'status': 200,
                    'data': SkillAreaDetailSerializer(skill_area).data,
                    'message': 'Skill area updated successfully'
                })
            return response({'status': 400, 'message': 'Validation error', 'errors': serializer.errors})
        except SkillArea.DoesNotExist:
            return response({'status': 404, 'message': 'Skill area not found'})
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'SkillArea')
    )
    def destroy(self, request, pk=None):
        """Delete a skill area"""
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Only admins can delete skill areas'})
        
        try:
            skill_area = self.get_object()
            
            # Check if there are enrolled learners
            if skill_area.total_enrolled > 0:
                return response({
                    'status': 400,
                    'message': 'Cannot delete skill area with enrolled learners. Archive it instead.'
                })
            
            skill_area_name = skill_area.name
            skill_area.delete()
            return response({
                'status': 200,
                'message': f'Skill area "{skill_area_name}" deleted successfully'
            })
        except SkillArea.DoesNotExist:
            return response({'status': 404, 'message': 'Skill area not found'})
    
    @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'SkillArea')
    )
    def update_metrics(self, request, pk=None):
        """Manually update skill area metrics"""
        if request.user.role not in [User.Role.ADMIN, User.Role.FACILITATOR]:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        try:
            skill_area = self.get_object()
            skill_area.update_metrics()
            return response({
                'status': 200,
                'message': 'Metrics updated successfully',
                'data': {
                    'total_enrolled': skill_area.total_enrolled,
                    'avg_completion_rate': float(skill_area.avg_completion_rate),
                    'total_modules': skill_area.total_modules
                }
            })
        except SkillArea.DoesNotExist:
            return response({'status': 404, 'message': 'Skill area not found'})
    
    @action(detail=True, methods=['get'])
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'Analytics')
    )
    def analytics(self, request, pk=None):
        """Get detailed analytics for a skill area"""
        try:
            skill_area = self.get_object()
            
            # Get learner enrollment by month
            from fme.models.learner import LearnerProfile
            from datetime import timedelta
            
            now = timezone.now()
            monthly_data = []
            
            for i in range(12):
                month_start = now - timedelta(days=30 * (i + 1))
                month_end = now - timedelta(days=30 * i)
                
                enrollments = LearnerProfile.objects.filter(
                    learning_track=skill_area.name,
                    created_at__gte=month_start,
                    created_at__lt=month_end
                ).count()
                
                monthly_data.append({
                    'month': month_start.strftime('%Y-%m'),
                    'enrollments': enrollments
                })
            
            # Performance by state
            state_performance = LearnerProfile.objects.filter(
                learning_track=skill_area.name
            ).values('state').annotate(
                learner_count=Count('id'),
                avg_progress=Avg('progress')
            ).order_by('-learner_count')[:10]
            
            analytics_data = {
                'enrollment_trend': monthly_data[::-1],
                'state_performance': list(state_performance),
                'module_completion_rates': [
                    {
                        'module_name': module.name,
                        'completion_rate': float(module.completion_rate)
                    } for module in skill_area.modules.all()
                ],
                'learner_demographics': {
                    'by_account_type': list(
                        LearnerProfile.objects.filter(learning_track=skill_area.name)
                        .values('account_type').annotate(count=Count('id'))
                    ),
                    'by_work_type': list(
                        LearnerProfile.objects.filter(learning_track=skill_area.name)
                        .values('work_type').annotate(count=Count('id'))
                    )
                }
            }
            
            return response({'status': 200, 'data': analytics_data})
            
        except SkillArea.DoesNotExist:
            return response({'status': 404, 'message': 'Skill area not found'})


class SkillAreaStatsView(BaseAuthorizationView):
    """
    View for skill area statistics and overview
    """
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'SkillAreaStats')
    )
    def get(self, request):
        """Get overall skill area statistics"""
        
        # Basic counts
        total_skill_areas = SkillArea.objects.count()
        active_skill_areas = SkillArea.objects.filter(status=SkillArea.Status.ACTIVE).count()
        draft_skill_areas = SkillArea.objects.filter(status=SkillArea.Status.DRAFT).count()
        total_modules = SkillAreaModule.objects.count()
        
        # Enrollment stats
        total_enrolled = SkillArea.objects.aggregate(
            total=Sum('total_enrolled')  #sum
        )['total'] or 0
        
        # Average completion rate
        avg_completion = SkillArea.objects.aggregate(
            avg=Avg('avg_completion_rate')
        )['avg'] or 0
        
        # Top performing skill areas
        top_performing = SkillArea.objects.filter(
            status=SkillArea.Status.ACTIVE
        ).order_by('-avg_completion_rate')[:5].values(
            'name', 'avg_completion_rate', 'total_enrolled'
        )
        
        # Most popular skill areas
        popular_areas = SkillArea.objects.filter(
            status=SkillArea.Status.ACTIVE
        ).order_by('-total_enrolled')[:5].values(
            'name', 'total_enrolled', 'avg_completion_rate'
        )
        
        stats = {
            'total_skill_areas': total_skill_areas,
            'active_skill_areas': active_skill_areas,
            'draft_skill_areas': draft_skill_areas,
            'total_modules': total_modules,
            'total_enrolled_learners': total_enrolled,
            'average_completion_rate': round(avg_completion, 2),
            'top_performing_areas': list(top_performing),
            'popular_areas': list(popular_areas)
        }
        
        return response({'status': 200, 'data': stats})


class SkillAreaModuleView(BaseAuthorizationView, PaginationHandlerMixin):
    """
    View for managing skill area modules
    """
    
    @swagger_auto_schema(
        query_serializer=PaginationParamSerializer,
        responses=swagger_data.doc_response('empty', 'SkillAreaModule')
    )
    def get(self, request, skill_area_id):
        """Get modules for a specific skill area"""
        try:
            skill_area = SkillArea.objects.get(id=skill_area_id)
            modules = skill_area.modules.all().order_by('order')
            
            # Apply pagination
            page_size = request.query_params.get('page_size', settings.DEFAULT_PAGINATION_SIZE)
            self.page_size = int(page_size)
            
            paginated_modules = self.paginate_queryset(modules, request, view=self)
            serializer = SkillAreaModuleSerializer(paginated_modules, many=True)
            
            paginated_response = self.get_paginated_response(serializer.data)
            return response({'status': 200, 'data': paginated_response})
            
        except SkillArea.DoesNotExist:
            return response({'status': 404, 'message': 'Skill area not found'})
    
    @swagger_auto_schema(
        request_body=SkillAreaModuleSerializer,
        responses=swagger_data.doc_response('empty', 'SkillAreaModule')
    )
    def post(self, request, skill_area_id):
        """Create a new module for a skill area"""
        if request.user.role not in [User.Role.ADMIN, User.Role.FACILITATOR]:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        try:
            skill_area = SkillArea.objects.get(id=skill_area_id)
            serializer = SkillAreaModuleSerializer(data=request.data)
            
            if serializer.is_valid():
                module = serializer.save(skill_area=skill_area)
                return response({
                    'status': 201,
                    'data': SkillAreaModuleSerializer(module).data,
                    'message': 'Module created successfully'
                })
            return response({'status': 400, 'message': 'Validation error', 'errors': serializer.errors})
            
        except SkillArea.DoesNotExist:
            return response({'status': 404, 'message': 'Skill area not found'})
    
    @swagger_auto_schema(
        request_body=SkillAreaModuleSerializer,
        responses=swagger_data.doc_response('empty', 'SkillAreaModule')
    )
    def put(self, request, skill_area_id, module_id):
        """Update a specific module"""
        if request.user.role not in [User.Role.ADMIN, User.Role.FACILITATOR]:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        try:
            module = SkillAreaModule.objects.get(id=module_id, skill_area_id=skill_area_id)
            serializer = SkillAreaModuleSerializer(module, data=request.data, partial=True)
            
            if serializer.is_valid():
                module = serializer.save()
                return response({
                    'status': 200,
                    'data': SkillAreaModuleSerializer(module).data,
                    'message': 'Module updated successfully'
                })
            return response({'status': 400, 'message': 'Validation error', 'errors': serializer.errors})
            
        except SkillAreaModule.DoesNotExist:
            return response({'status': 404, 'message': 'Module not found'})
    
    @swagger_auto_schema(
        responses=swagger_data.doc_response('empty', 'SkillAreaModule')
    )
    def delete(self, request, skill_area_id, module_id):
        """Delete a specific module"""
        if request.user.role != User.Role.ADMIN:
            return response({'status': 403, 'message': 'Only admins can delete modules'})
        
        try:
            module = SkillAreaModule.objects.get(id=module_id, skill_area_id=skill_area_id)
            module_name = module.name
            module.delete()
            
            return response({
                'status': 200,
                'message': f'Module "{module_name}" deleted successfully'
            })
            
        except SkillAreaModule.DoesNotExist:
            return response({'status': 404, 'message': 'Module not found'})


class BulkSkillAreaActionView(BaseAuthorizationView):
    """
    View for bulk operations on skill areas
    """
    
    @swagger_auto_schema(
        request_body=BulkSkillAreaActionSerializer,
        responses=swagger_data.doc_response('empty', 'BulkAction')
    )
    def post(self, request):
        """Perform bulk actions on skill areas"""
        if request.user.role not in [User.Role.ADMIN, User.Role.FACILITATOR]:
            return response({'status': 403, 'message': 'Unauthorized access'})
        
        serializer = BulkSkillAreaActionSerializer(data=request.data)
        if serializer.is_valid():
            skill_area_ids = serializer.validated_data['skill_area_ids']
            action = serializer.validated_data['action']
            reason = serializer.validated_data.get('reason', '')
            
            try:
                skill_areas = SkillArea.objects.filter(id__in=skill_area_ids)
                
                if action == 'activate':
                    updated_count = skill_areas.update(status=SkillArea.Status.ACTIVE)
                elif action == 'draft':
                    updated_count = skill_areas.update(status=SkillArea.Status.DRAFT)
                elif action == 'archive':
                    updated_count = skill_areas.update(status=SkillArea.Status.ARCHIVED)
                elif action == 'delete':
                    if request.user.role != User.Role.ADMIN:
                        return response({'status': 403, 'message': 'Only admins can delete skill areas'})
                    
                    # Check for enrolled learners
                    areas_with_learners = skill_areas.filter(total_enrolled__gt=0).count()
                    if areas_with_learners > 0:
                        return response({
                            'status': 400,
                            'message': f'{areas_with_learners} skill areas have enrolled learners and cannot be deleted'
                        })
                    
                    updated_count = skill_areas.count()
                    skill_areas.delete()
                else:
                    return response({'status': 400, 'message': 'Invalid action'})
                
                return response({
                    'status': 200,
                    'data': {
                        'message': f'Successfully {action}d {updated_count} skill areas',
                        'affected_count': updated_count,
                        'action': action
                    }
                })
                
            except Exception as e:
                return response({'status': 400, 'message': f'Bulk operation failed: {str(e)}'})
        
        return response({'status': 400, 'message': 'Validation error', 'errors': serializer.errors})


class LearnerProgressView(BaseAuthorizationView, PaginationHandlerMixin):
    """
    View for managing learner progress in skill areas
    """
    
    @swagger_auto_schema(
        query_serializer=PaginationParamSerializer,
        responses=swagger_data.doc_response('empty', 'LearnerProgress')
    )
    def get(self, request, skill_area_id=None):
        """Get learner progress data"""
        
        if skill_area_id:
            # Get progress for specific skill area
            try:
                skill_area = SkillArea.objects.get(id=skill_area_id)
                progress_records = LearnerSkillAreaProgress.objects.filter(
                    skill_area=skill_area
                ).select_related('learner', 'learner__user')
                
            except SkillArea.DoesNotExist:
                return response({'status': 404, 'message': 'Skill area not found'})
        else:
            # Get all progress records
            progress_records = LearnerSkillAreaProgress.objects.all().select_related(
                'learner', 'learner__user', 'skill_area'
            )
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            progress_records = progress_records.filter(status=status_filter)
        
        # Apply pagination
        page_size = request.query_params.get('page_size', settings.DEFAULT_PAGINATION_SIZE)
        self.page_size = int(page_size)
        
        paginated_records = self.paginate_queryset(progress_records, request, view=self)
        serializer = LearnerSkillAreaProgressSerializer(paginated_records, many=True)
        
        paginated_response = self.get_paginated_response(serializer.data)
        return response({'status': 200, 'data': paginated_response})


class SkillAreaExportView(BaseAuthorizationView):
    """
    View for exporting skill area data
    """
    
    def get(self, request):
        """Export skill areas data to CSV"""
        import csv
        from django.http import HttpResponse
        
        response_obj = HttpResponse(content_type='text/csv')
        response_obj['Content-Disposition'] = 'attachment; filename="skill_areas_export.csv"'
        
        writer = csv.writer(response_obj)
        
        # Write header
        writer.writerow([
            'Name', 'Status', 'Target Audience', 'Total Enrolled',
            'Completion Rate (%)', 'Total Modules', 'Duration (weeks)',
            'Created Date', 'Created By'
        ])
        
        # Write data
        skill_areas = SkillArea.objects.select_related('created_by').all()
        
        for area in skill_areas:
            writer.writerow([
                area.name,
                area.get_status_display(),
                area.get_target_audience_display(),
                area.total_enrolled,
                float(area.avg_completion_rate),
                area.total_modules,
                area.estimated_duration_weeks,
                area.created_at.strftime('%Y-%m-%d'),
                area.created_by.get_full_name() if area.created_by else 'System'
            ])
        
        return response_obj