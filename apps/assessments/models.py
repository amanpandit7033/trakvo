from django.db import models
from apps.institutes.models import Batch
from apps.students.models import Student
from django.contrib.auth import get_user_model

User = get_user_model()

class Test(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='tests')
    name = models.CharField(max_length=255)
    test_date = models.DateField()
    max_marks = models.DecimalField(max_digits=6, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tests')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.batch.name} ({self.test_date})"

class TestResult(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='test_results')
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('test', 'student')

    def __str__(self):
        return f"{self.student.full_name} - {self.test.name} - {self.marks_obtained}/{self.test.max_marks}"
