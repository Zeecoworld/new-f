from django.db import models
from fme.models.base import BaseModel
from fme.models.user import User
from fme.models.learner import LearnerProfile


class SkillArea(BaseModel):
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'
    
    class TargetAudience(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    target_audience = models.CharField(max_length=20, choices=TargetAudience.choices, default=TargetAudience.BEGINNER)
    total_enrolled = models.PositiveIntegerField(default=0)
    avg_completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_modules = models.PositiveIntegerField(default=0)
    image = models.URLField(blank=True, null=True)
    prerequisites = models.TextField(blank=True, help_text="Prerequisites for this skill area")
    learning_objectives = models.TextField(blank=True, help_text="What learners will achieve")
    estimated_duration_weeks = models.PositiveIntegerField(default=12)
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_skill_areas'
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['target_audience']),
            models.Index(fields=['avg_completion_rate']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE
    
    def update_metrics(self):
        enrolled_count = LearnerProfile.objects.filter(learning_track=self.name).count()
        learners = LearnerProfile.objects.filter(learning_track=self.name)
        if learners.exists():
            avg_progress = learners.aggregate(
                models.Avg('progress')
            )['progress__avg'] or 0
        else:
            avg_progress = 0
        active_modules = self.modules.filter(status=SkillAreaModule.Status.ACTIVE).count()
        self.total_enrolled = enrolled_count
        self.avg_completion_rate = round(avg_progress, 2)
        self.total_modules = active_modules
        self.save(update_fields=['total_enrolled', 'avg_completion_rate', 'total_modules'])


class SkillAreaModule(BaseModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        ACTIVE = 'ACTIVE', 'Active'
        ARCHIVED = 'ARCHIVED', 'Archived'
    
    class Level(models.TextChoices):
        BEGINNER = 'BEGINNER', 'Beginner'
        INTERMEDIATE = 'INTERMEDIATE', 'Intermediate'
        ADVANCED = 'ADVANCED', 'Advanced'
    
    skill_area = models.ForeignKey(
        SkillArea, 
        on_delete=models.CASCADE, 
        related_name='modules'
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=Level.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    order = models.PositiveIntegerField(default=0)
    duration_hours = models.PositiveIntegerField(default=10)
    learning_objectives = models.TextField(help_text="What learners will learn in this module")
    prerequisites = models.TextField(blank=True, help_text="Prerequisites for this module")
    resources = models.JSONField(default=dict, help_text="Additional resources and links")

    completion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    class Meta:
        ordering = ['skill_area', 'order']
        unique_together = ['skill_area', 'name']
        indexes = [
            models.Index(fields=['skill_area', 'order']),
            models.Index(fields=['level']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.skill_area.name} - {self.name}"


class LearnerSkillAreaProgress(BaseModel):
    
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
        PAUSED = 'PAUSED', 'Paused'
    
    learner = models.ForeignKey(
        'LearnerProfile', 
        on_delete=models.CASCADE, 
        related_name='skill_area_progress'
    )
    skill_area = models.ForeignKey(
        SkillArea, 
        on_delete=models.CASCADE, 
        related_name='learner_progress'
    )
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    total_time_spent_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    current_module = models.ForeignKey(
        SkillAreaModule, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    class Meta:
        unique_together = ['learner', 'skill_area']
        indexes = [
            models.Index(fields=['learner', 'status']),
            models.Index(fields=['skill_area', 'status']),
            models.Index(fields=['progress_percentage']),
        ]
    
    def __str__(self):
        return f"{self.learner.user.get_full_name()} - {self.skill_area.name} ({self.progress_percentage}%)"


class LearnerModuleProgress(BaseModel):
    
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        COMPLETED = 'COMPLETED', 'Completed'
    
    learner = models.ForeignKey(
        'LearnerProfile', 
        on_delete=models.CASCADE, 
        related_name='module_progress'
    )
    module = models.ForeignKey(
        SkillAreaModule, 
        on_delete=models.CASCADE, 
        related_name='learner_progress'
    )
    skill_area_progress = models.ForeignKey(
        LearnerSkillAreaProgress, 
        on_delete=models.CASCADE, 
        related_name='module_progress'
    )
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_hours = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    # Performance data
    attempts = models.PositiveIntegerField(default=0)
    best_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['learner', 'module']
        indexes = [
            models.Index(fields=['learner', 'status']),
            models.Index(fields=['module', 'status']),
            models.Index(fields=['progress_percentage']),
        ]
    
    def __str__(self):
        return f"{self.learner.user.get_full_name()} - {self.module.name} ({self.progress_percentage}%)"


# class SkillAreaAssessment(BaseModel):???
#     """Assessments for skill areas"""
    
#     class AssessmentType(models.TextChoices):
#         QUIZ = 'QUIZ', 'Quiz'
#         PROJECT = 'PROJECT', 'Project'
#         ASSIGNMENT = 'ASSIGNMENT', 'Assignment'
#         FINAL_EXAM = 'FINAL_EXAM', 'Final Exam'
    
#     skill_area = models.ForeignKey(
#         SkillArea, 
#         on_delete=models.CASCADE, 
#         related_name='assessments'
#     )
#     module = models.ForeignKey(
#         SkillAreaModule, 
#         on_delete=models.CASCADE, 
#         null=True, 
#         blank=True, 
#         related_name='assessments'
#     )
    
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     assessment_type = models.CharField(max_length=20, choices=AssessmentType.choices)
    
#     # Configuration
#     max_score = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
#     passing_score = models.DecimalField(max_digits=5, decimal_places=2, default=70.00)
#     time_limit_minutes = models.PositiveIntegerField(null=True, blank=True)
#     max_attempts = models.PositiveIntegerField(default=3)
    
#     # Scheduling
#     is_active = models.BooleanField(default=True)
#     available_from = models.DateTimeField(null=True, blank=True)
#     available_until = models.DateTimeField(null=True, blank=True)
    
#     # Content
#     instructions = models.TextField(blank=True)
#     questions = models.JSONField(default=list, help_text="Assessment questions and answers")
    
#     class Meta:
#         ordering = ['skill_area', 'module', 'title']
#         indexes = [
#             models.Index(fields=['skill_area', 'is_active']),
#             models.Index(fields=['assessment_type']),
#         ]
    
#     def __str__(self):
#         return f"{self.skill_area.name} - {self.title}"