from django.contrib import admin
from .models import Assignment, ExampleTestCase, TestCase, Submission, Feedback

# Register your models here.
admin.site.register(Assignment)
admin.site.register(ExampleTestCase)
admin.site.register(TestCase)
admin.site.register(Submission)
admin.site.register(Feedback)