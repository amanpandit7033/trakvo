from django.db import models
from apps.students.models import Student
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()

class FeeStructure(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_structures')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    installment_label = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_paid(self):
        return sum(payment.amount_paid for payment in self.payments.all()) or Decimal('0.00')

    @property
    def balance_due(self):
        return self.total_amount - self.total_paid

    @property
    def status(self):
        if self.balance_due <= 0:
            return 'paid'
        elif self.total_paid > 0:
            return 'partial'
        else:
            return 'pending'

    def __str__(self):
        return f"{self.student.full_name} - {self.installment_label or 'Fee'} - {self.total_amount}"

class Payment(models.Model):
    PAYMENT_MODES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('other', 'Other'),
    ]

    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_payments')
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.amount_paid} via {self.payment_mode} on {self.payment_date}"
