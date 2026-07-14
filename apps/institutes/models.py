from django.db import models

class Institute(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='institute_logos/', null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, default='Patna')
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_suspended = models.BooleanField(default=False)
    trial_ends_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Batch(models.Model):
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='batches')
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
