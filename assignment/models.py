from django.db import models
from course_management.models import Course
from account.models import CustomUser
from django.db import transaction
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    max_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    programming_language = models.CharField(null=True)
    language_id = models.IntegerField()
    is_draft = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='assignments')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at']


class TestCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='test_cases')
    input = models.CharField(max_length=100)
    output = models.CharField(max_length=100)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.assignment.title} - {self.input}'


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.TextField()
    score = models.FloatField()
    is_best = models.BooleanField(default=False)
    results = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.assignment.title} - {self.student.email}'

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['assignment', 'student', 'is_best']),
            models.Index(fields=['student', 'assignment'])
        ]
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            previous_best_submission = Submission.objects.filter(
                assignment=self.assignment,
                student=self.student,
                is_best=True
            ).select_for_update().first()

            if not previous_best_submission or self.score >= previous_best_submission.score:
                Submission.objects.filter(
                    student=self.student,
                    assignment=self.assignment
                ).update(is_best=False)

                self.is_best = True
            else:
                self.is_best = False
        super().save(*args, **kwargs)


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']
