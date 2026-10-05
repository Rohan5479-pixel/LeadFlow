from django.contrib import admin
from .models import (
    Course,
    Counselor,
    Lead,
    Trainer,
    Batch,
    Student,
    Subject,
    Certification,
    Enrollment,
    Feedback
)


admin.site.register(Course)
admin.site.register(Counselor)
admin.site.register(Lead)
admin.site.register(Trainer)
admin.site.register(Batch)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Certification)
admin.site.register(Enrollment)
admin.site.register(Feedback)