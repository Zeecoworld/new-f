from rest_framework import serializers
from fme.models.user import User
from fme.serializers.base import BaseSerializer

class BulkUserActionSerializer(BaseSerializer):
    """Serializer for bulk user operations"""
    action = serializers.ChoiceField(
        choices=['activate', 'deactivate', 'disable'],
        help_text="Action to perform on selected users"
    )
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of user IDs to perform action on"
    )
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Optional reason for the bulk action"
    )

class UserStatusUpdateSerializer(serializers.Serializer):
    """Enhanced user status update serializer"""
    user_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=User.Status.choices)
    reason = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Reason for status change"
    )
    notify_user = serializers.BooleanField(
        default=False,
        help_text="Whether to notify user about status change"
    )

class DashboardFilterSerializer(BaseSerializer):
    """Common dashboard filters"""
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    period = serializers.ChoiceField(
        choices=['week', 'month', 'quarter', 'year'],
        default='month',
        required=False
    )

class LearnerProgressUpdateSerializer(BaseSerializer):
    """Serializer for updating learner progress"""
    learner_id = serializers.UUIDField()
    progress = serializers.IntegerField(min_value=0, max_value=100)
    notes = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Optional notes about progress update"
    )

class InviteUserSerializer(BaseSerializer):
    """Serializer for inviting new users"""
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=User.Role.choices)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    custom_message = serializers.CharField(
        max_length=1000,
        required=False,
        help_text="Custom invitation message"
    )

class SystemNotificationSerializer(BaseSerializer):
    """Serializer for system-wide notifications"""
    title = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=1000)
    notification_type = serializers.ChoiceField(
        choices=['info', 'warning', 'success', 'error'],
        default='info'
    )
    target_roles = serializers.ListField(
        child=serializers.ChoiceField(choices=User.Role.choices),
        required=False,
        help_text="Specific roles to notify (all users if empty)"
    )
    expires_at = serializers.DateTimeField(
        required=False,
        help_text="When the notification should expire"
    )

class LearnerAssignmentSerializer(BaseSerializer):
    """Serializer for assigning learner to mentor/facilitator"""
    learner_id = serializers.UUIDField()
    mentor_id = serializers.UUIDField(required=False)
    facilitator_id = serializers.UUIDField(required=False)
    assignment_type = serializers.ChoiceField(
        choices=['mentor', 'facilitator'],
        help_text="Type of assignment"
    )
    notes = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Assignment notes"
    )

    def validate(self, data):
        assignment_type = data.get('assignment_type')
        if assignment_type == 'mentor' and not data.get('mentor_id'):
            raise serializers.ValidationError("mentor_id is required when assignment_type is 'mentor'")
        if assignment_type == 'facilitator' and not data.get('facilitator_id'):
            raise serializers.ValidationError("facilitator_id is required when assignment_type is 'facilitator'")
        return data

class ReportGenerationSerializer(BaseSerializer):
    """Serializer for generating reports"""
    report_type = serializers.ChoiceField(
        choices=['learners', 'mentors', 'facilitators', 'progress', 'analytics'],
        help_text="Type of report to generate"
    )
    format = serializers.ChoiceField(
        choices=['csv', 'excel', 'pdf'],
        default='csv',
        help_text="Output format"
    )
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)
    filters = serializers.DictField(
        required=False,
        help_text="Additional filters for the report"
    )
    include_analytics = serializers.BooleanField(
        default=False,
        help_text="Include analytics data in report"
    )

class LearnerBulkOperationSerializer(BaseSerializer):
    """Serializer for bulk operations on learners"""
    learner_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of learner IDs"
    )
    operation = serializers.ChoiceField(
        choices=['update_progress', 'assign_mentor', 'send_message', 'export'],
        help_text="Operation to perform"
    )
    operation_data = serializers.DictField(
        required=False,
        help_text="Additional data for the operation"
    )

class DashboardWidgetSerializer(BaseSerializer):
    """Serializer for dashboard widget configuration"""
    widget_id = serializers.CharField(max_length=50)
    position = serializers.IntegerField(min_value=0)
    size = serializers.ChoiceField(choices=['small', 'medium', 'large'])
    visible = serializers.BooleanField(default=True)
    refresh_interval = serializers.IntegerField(
        min_value=30,
        max_value=3600,
        default=300,
        help_text="Refresh interval in seconds"
    )

class ActivityLogFilterSerializer(BaseSerializer):
    """Serializer for filtering activity logs"""
    user_id = serializers.UUIDField(required=False)
    action_type = serializers.CharField(max_length=50, required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    page = serializers.IntegerField(min_value=1, default=1)
    page_size = serializers.IntegerField(min_value=1, max_value=100, default=20)

class LearnerSearchSerializer(BaseSerializer):
    """Advanced learner search serializer"""
    query = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Search query (name, email, phone)"
    )
    state = serializers.CharField(max_length=25, required=False)
    learning_track = serializers.CharField(max_length=100, required=False)
    progress_range = serializers.CharField(
        max_length=20,
        required=False,
        help_text="Progress range in format 'min-max' (e.g., '50-80')"
    )
    registration_period = serializers.ChoiceField(
        choices=['last_week', 'last_month', 'last_quarter', 'last_year'],
        required=False
    )
    status = serializers.ChoiceField(
        choices=User.Status.choices,
        required=False
    )
    sort_by = serializers.ChoiceField(
        choices=['name', 'progress', 'registration_date', 'last_active'],
        default='registration_date'
    )
    sort_order = serializers.ChoiceField(
        choices=['asc', 'desc'],
        default='desc'
    )

class MentorPerformanceSerializer(BaseSerializer):
    """Serializer for mentor performance metrics"""
    mentor_id = serializers.UUIDField()
    period = serializers.ChoiceField(
        choices=['month', 'quarter', 'year'],
        default='month'
    )
    include_mentees = serializers.BooleanField(
        default=True,
        help_text="Include mentee details in response"
    )