from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.students.models import Student
from apps.institutes.models import Batch
from django.contrib.auth import get_user_model

User = get_user_model()

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendance')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def clean(self):
        super().clean()
        if self.date and self.date > timezone.now().date():
            raise ValidationError("Cannot mark attendance for a future date.")

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"
