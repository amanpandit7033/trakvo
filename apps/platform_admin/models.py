from django.db import models
from apps.accounts.models import CustomUser
from apps.institutes.models import Institute

class PlatformPayment(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='platform_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    notes = models.CharField(max_length=255, blank=True)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='recorded_platform_payments')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.institute.name} - ₹{self.amount}"

class ActivityLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activity_logs')
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, null=True, blank=True, related_name='platform_activity_logs')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.action}"
