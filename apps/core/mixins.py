from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.contrib import messages

class OwnerRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'owner':
            messages.error(request, "You don't have access to this page.")
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

class TeacherRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'teacher':
            messages.error(request, "You don't have access to this page.")
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)

class SuperAdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'super_admin':
            messages.error(request, "You don't have access to this page.")
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)
