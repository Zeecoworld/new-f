from rest_framework import serializers
from fme.models.skill_area import (
    SkillArea, SkillAreaModule, LearnerSkillAreaProgress, 
    LearnerModuleProgress, SkillAreaAssessment
)
from fme.models.user import User
from fme.serializers.base import BaseSerializer
from fme.serializers.authentication import UserSerializer


class SkillAreaModuleSerializer(serializers.ModelSerializer):
    """Serializer for skill area modules"""
    level_display = serializers.CharField(source='get_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SkillAreaModule
        fields = [
            'id', 'name', 'description', 'level', 'level_display', 
            'status', 'status_display', 'order', 'duration_hours',
            'learning_objectives', 'prerequisites', 'resources',
            'completion_rate', 'average_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'completion_rate', 'average_score', 'created_at', 'updated_at']


class SkillAreaCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating skill areas"""
    modules = SkillAreaModuleSerializer(many=True, required=False)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = SkillArea
        fields = [
            'id', 'name', 'description', 'status', 'target_audience',
            'prerequisites', 'learning_objectives', 'estimated_duration_weeks',
            'image', 'modules', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'total_enrolled', 'avg_completion_rate', 'total_modules']
    
    def create(self, validated_data):
        modules_data = validated_data.pop('modules', [])
        validated_data['created_by'] = self.context['request'].user
        skill_area = SkillArea.objects.create(**validated_data)
        
        # Create modules
        for module_data in modules_data:
            SkillAreaModule.objects.create(skill_area=skill_area, **module_data)
        
        return skill_area
    
    def update(self, instance, validated_data):
        modules_data = validated_data.pop('modules', None)
        
        # Update skill area
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update modules if provided
        if modules_data is not None:
            # Clear existing modules and create new ones
            instance.modules.all().delete()
            for module_data in modules_data:
                SkillAreaModule.objects.create(skill_area=instance, **module_data)
        
        return instance


class SkillAreaListSerializer(serializers.ModelSerializer):
    """Serializer for skill area list view"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    target_audience_display = serializers.CharField(source='get_target_audience_display', read_only=True)
    created_by = UserSerializer(read_only=True)
    modules_count = serializers.IntegerField(source='modules.count', read_only=True)
    active_modules_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SkillArea
        fields = [
            'id', 'name', 'slug', 'description', 'status', 'status_display',
            'target_audience', 'target_audience_display', 'total_enrolled',
            'avg_completion_rate', 'total_modules', 'modules_count',
            'active_modules_count', 'estimated_duration_weeks',
            'created_by', 'created_at', 'updated_at'
        ]
    
    def get_active_modules_count(self, obj):
        return obj.modules.filter(status=SkillAreaModule.Status.ACTIVE).count()


class SkillAreaDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual skill area view"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    target_audience_display = serializers.CharField(source='get_target_audience_display', read_only=True)
    modules = SkillAreaModuleSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    
    # Analytics data
    enrollment_trend = serializers.SerializerMethodField()
    completion_stats = serializers.SerializerMethodField()
    performance_by_module = serializers.SerializerMethodField()
    
    class Meta:
        model = SkillArea
        fields = [
            'id', 'name', 'slug', 'description', 'status', 'status_display',
            'target_audience', 'target_audience_display', 'prerequisites',
            'learning_objectives', 'estimated_duration_weeks', 'image',
            'total_enrolled', 'avg_completion_rate', 'total_modules',
            'modules', 'created_by', 'enrollment_trend', 'completion_stats',
            'performance_by_module', 'created_at', 'updated_at'
        ]
    
    def get_enrollment_trend(self, obj):
        """Get enrollment trend data for the last 6 months"""
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Count
        from fme.models.learner import LearnerProfile
        
        now = timezone.now()
        trend_data = []
        
        for i in range(6):
            month_start = now - timedelta(days=30 * (i + 1))
            month_end = now - timedelta(days=30 * i)
            
            count = LearnerProfile.objects.filter(
                learning_track=obj.name,
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            
            trend_data.append({
                'month': month_start.strftime('%Y-%m'),
                'enrollments': count
            })
        
        return trend_data[::-1]  # Reverse for chronological order
    
    def get_completion_stats(self, obj):
        """Get completion statistics"""
        from fme.models.learner import LearnerProfile
        
        learners = LearnerProfile.objects.filter(learning_track=obj.name)
        total = learners.count()
        
        if total == 0:
            return {
                'total_learners': 0,
                'completed': 0,
                'in_progress': 0,
                'not_started': 0,
                'completion_rate': 0
            }
        
        completed = learners.filter(progress=100).count()
        in_progress = learners.filter(progress__gt=0, progress__lt=100).count()
        not_started = learners.filter(progress=0).count()
        
        return {
            'total_learners': total,
            'completed': completed,
            'in_progress': in_progress,
            'not_started': not_started,
            'completion_rate': round((completed / total) * 100, 2)
        }
    
    def get_performance_by_module(self, obj):
        """Get performance data by module"""
        modules_performance = []
        
        for module in obj.modules.filter(status=SkillAreaModule.Status.ACTIVE):
            # This would require more complex queries with actual progress tracking
            modules_performance.append({
                'module_name': module.name,
                'level': module.level,
                'completion_rate': float(module.completion_rate),
                'average_score': float(module.average_score),
                'duration_hours': module.duration_hours
            })
        
        return modules_performance


class LearnerSkillAreaProgressSerializer(serializers.ModelSerializer):
    """Serializer for learner skill area progress"""
    skill_area = SkillAreaListSerializer(read_only=True)
    learner = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_module = SkillAreaModuleSerializer(read_only=True)
    
    class Meta:
        model = LearnerSkillAreaProgress
        fields = [
            'id', 'learner', 'skill_area', 'status', 'status_display',
            'progress_percentage', 'started_at', 'completed_at',
            'last_accessed_at', 'total_time_spent_hours', 'current_module'
        ]
        read_only_fields = ['id', 'learner', 'last_accessed_at']


class LearnerModuleProgressSerializer(serializers.ModelSerializer):
    """Serializer for learner module progress"""
    module = SkillAreaModuleSerializer(read_only=True)
    learner = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LearnerModuleProgress
        fields = [
            'id', 'learner', 'module', 'status', 'status_display',
            'progress_percentage', 'score', 'best_score', 'started_at',
            'completed_at', 'time_spent_hours', 'attempts', 'notes'
        ]
        read_only_fields = ['id', 'learner']


class SkillAreaAssessmentSerializer(serializers.ModelSerializer):
    """Serializer for skill area assessments"""
    skill_area = serializers.StringRelatedField(read_only=True)
    module = serializers.StringRelatedField(read_only=True)
    assessment_type_display = serializers.CharField(source='get_assessment_type_display', read_only=True)
    
    class Meta:
        model = SkillAreaAssessment
        fields = [
            'id', 'skill_area', 'module', 'title', 'description',
            'assessment_type', 'assessment_type_display', 'max_score',
            'passing_score', 'time_limit_minutes', 'max_attempts',
            'is_active', 'available_from', 'available_until',
            'instructions', 'questions'
        ]
        read_only_fields = ['id']


class SkillAreaFilterSerializer(BaseSerializer):
    """Serializer for filtering skill areas"""
    status = serializers.ChoiceField(choices=SkillArea.Status.choices, required=False)
    target_audience = serializers.ChoiceField(choices=SkillArea.TargetAudience.choices, required=False)
    search = serializers.CharField(max_length=200, required=False)
    created_by = serializers.UUIDField(required=False)
    min_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    max_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    ordering = serializers.ChoiceField(
        choices=['name', '-name', 'created_at', '-created_at', 'avg_completion_rate', '-avg_completion_rate'],
        default='-created_at',
        required=False
    )


class SkillAreaStatsSerializer(BaseSerializer):
    """Serializer for skill area statistics"""
    total_skill_areas = serializers.IntegerField(read_only=True)
    active_skill_areas = serializers.IntegerField(read_only=True)
    draft_skill_areas = serializers.IntegerField(read_only=True)
    total_modules = serializers.IntegerField(read_only=True)
    total_enrolled_learners = serializers.IntegerField(read_only=True)
    average_completion_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    top_performing_areas = serializers.ListField(read_only=True)
    popular_areas = serializers.ListField(read_only=True)


class BulkSkillAreaActionSerializer(BaseSerializer):
    """Serializer for bulk actions on skill areas"""
    skill_area_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of skill area IDs"
    )
    action = serializers.ChoiceField(
        choices=['activate', 'draft', 'archive', 'delete'],
        help_text="Action to perform"
    )
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Reason for the action"
    )