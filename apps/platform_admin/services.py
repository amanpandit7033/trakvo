from .models import ActivityLog

def log_activity(user, action, institute=None):
    ActivityLog.objects.create(
        user=user,
        action=action,
        institute=institute
    )
