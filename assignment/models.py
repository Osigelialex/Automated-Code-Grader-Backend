from django.db import models
from course_management.models import Course
from account.models import CustomUser
from django.core.validators import MaxValueValidator, MinValueValidator


class Assignment(models.Model):
    class ProgrammingLanguage(models.TextChoices):
        PYTHON = 'Python'
        JAVA = 'Java'
        CPP = 'C++'

    title = models.CharField(max_length=100)
    description = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    max_score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    programming_language = models.CharField(choices=ProgrammingLanguage.choices, max_length=10)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created_at']


class ExampleTestCase(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='example_test_cases')
    input = models.JSONField()
    output = models.JSONField()

    def __str__(self):
        return f'{self.assignment.title} - {self.input}'


class TestCase(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='test_cases')
    input = models.JSONField()
    output = models.JSONField()

    def __str__(self):
        return f'{self.assignment.title} - {self.input}'


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.TextField()
    score = models.FloatField()
    results = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.assignment.title} - {self.student.email}'

    class Meta:
        ordering = ['-submitted_at']


class Draft(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.assignment.title} - {self.student.email}'
