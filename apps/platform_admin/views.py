from django.views.generic import TemplateView, ListView, DetailView, CreateView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.utils.crypto import get_random_string

from apps.core.mixins import SuperAdminRequiredMixin
from apps.institutes.models import Institute
from apps.accounts.models import CustomUser
from apps.students.models import Student
from .models import PlatformPayment, ActivityLog
from .forms import PlatformPaymentForm, ExtendTrialForm
from .services import log_activity
from datetime import timedelta

class PlatformDashboardView(SuperAdminRequiredMixin, TemplateView):
    template_name = 'platform_admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_institutes'] = Institute.objects.count()
        context['active_institutes'] = Institute.objects.filter(is_suspended=False).count()
        context['suspended_institutes'] = Institute.objects.filter(is_suspended=True).count()
        context['total_students'] = Student.objects.filter(is_active=True).count()
        
        today = timezone.now().date()
        next_week = today + timedelta(days=7)
        context['trials_ending_soon'] = Institute.objects.filter(
            trial_ends_on__isnull=False,
            trial_ends_on__gte=today,
            trial_ends_on__lte=next_week,
            is_suspended=False
        ).order_by('trial_ends_on')
        
        context['recent_activity'] = ActivityLog.objects.select_related('user', 'institute').order_by('-timestamp')[:10]
        
        return context

class InstituteAdminListView(SuperAdminRequiredMixin, ListView):
    model = Institute
    template_name = 'platform_admin/institute_list.html'
    context_object_name = 'institutes'

    def get_queryset(self):
        qs = super().get_queryset().annotate(
            student_count=Count('students', filter=Q(students__is_active=True))
        )
        
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
            
        status = self.request.GET.get('status')
        if status == 'suspended':
            qs = qs.filter(is_suspended=True)
        elif status == 'active':
            qs = qs.filter(is_suspended=False)
            
        return qs.order_by('-created_at')

class InstituteAdminDetailView(SuperAdminRequiredMixin, DetailView):
    model = Institute
    template_name = 'platform_admin/institute_detail.html'
    context_object_name = 'institute'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        institute = self.object
        context['owners'] = CustomUser.objects.filter(institute=institute, role='owner')
        context['teachers'] = CustomUser.objects.filter(institute=institute, role='teacher')
        context['student_count'] = Student.objects.filter(institute=institute, is_active=True).count()
        context['batch_count'] = institute.batches.count()
        context['extend_trial_form'] = ExtendTrialForm(initial={'trial_ends_on': institute.trial_ends_on})
        return context

class SuspendInstituteView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        institute = get_object_or_404(Institute, pk=pk)
        action = request.POST.get('action')
        
        if action == 'suspend':
            institute.is_suspended = True
            log_activity(request.user, f"Suspended institute: {institute.name}", institute)
            messages.success(request, f"Institute {institute.name} suspended.")
        elif action == 'reactivate':
            institute.is_suspended = False
            log_activity(request.user, f"Reactivated institute: {institute.name}", institute)
            messages.success(request, f"Institute {institute.name} reactivated.")
            
        institute.save()
        return redirect('platform_admin:institute_detail', pk=pk)

class ExtendTrialView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        institute = get_object_or_404(Institute, pk=pk)
        form = ExtendTrialForm(request.POST)
        if form.is_valid():
            new_date = form.cleaned_data['trial_ends_on']
            institute.trial_ends_on = new_date
            institute.save()
            log_activity(request.user, f"Extended trial to {new_date}", institute)
            messages.success(request, "Trial extended successfully.")
        else:
            messages.error(request, f"Failed to extend trial: {form.errors.as_text()}")
        return redirect('platform_admin:institute_detail', pk=pk)

class UserAdminListView(SuperAdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'platform_admin/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        qs = CustomUser.objects.filter(role__in=['owner', 'teacher']).select_related('institute')
        
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(phone_number__icontains=search))
            
        role = self.request.GET.get('role')
        if role in ['owner', 'teacher']:
            qs = qs.filter(role=role)
            
        return qs.order_by('-date_joined')

class UserResetPasswordView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        new_password = get_random_string(length=8)
        user.set_password(new_password)
        user.save()
        log_activity(request.user, f"Reset password for {user.role}: {user.phone_number}", user.institute)
        messages.success(request, f"Password reset! The new temporary password is: {new_password}")
        return redirect('platform_admin:user_list')

class UserDeactivateView(SuperAdminRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = False
        user.save()
        log_activity(request.user, f"Deactivated {user.role}: {user.phone_number}", user.institute)
        messages.success(request, f"User {user.phone_number} deactivated.")
        return redirect('platform_admin:user_list')

class PlatformPaymentListView(SuperAdminRequiredMixin, ListView):
    model = PlatformPayment
    template_name = 'platform_admin/payment_list.html'
    context_object_name = 'payments'

    def get_queryset(self):
        self.institute = get_object_or_404(Institute, pk=self.kwargs['pk'])
        return PlatformPayment.objects.filter(institute=self.institute).order_by('-payment_date')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['institute'] = self.institute
        context['form'] = PlatformPaymentForm()
        return context

class PlatformPaymentCreateView(SuperAdminRequiredMixin, CreateView):
    model = PlatformPayment
    form_class = PlatformPaymentForm
    
    def form_valid(self, form):
        institute = get_object_or_404(Institute, pk=self.kwargs['pk'])
        form.instance.institute = institute
        form.instance.recorded_by = self.request.user
        response = super().form_valid(form)
        log_activity(self.request.user, f"Recorded manual payment of ₹{form.instance.amount}", institute)
        messages.success(self.request, "Payment recorded successfully.")
        return response
        
    def get_success_url(self):
        return reverse_lazy('platform_admin:payment_list', kwargs={'pk': self.kwargs['pk']})

class ActivityLogListView(SuperAdminRequiredMixin, ListView):
    model = ActivityLog
    template_name = 'platform_admin/activity_list.html'
    context_object_name = 'logs'
    paginate_by = 50

    def get_queryset(self):
        qs = ActivityLog.objects.select_related('user', 'institute').order_by('-timestamp')
        institute_id = self.request.GET.get('institute')
        if institute_id:
            qs = qs.filter(institute_id=institute_id)
        return qs

from .forms import InstituteCreationForm
from django.db import transaction

class InstituteCreateView(SuperAdminRequiredMixin, View):
    def get(self, request):
        form = InstituteCreationForm()
        return render(request, 'platform_admin/institute_form.html', {'form': form})

    def post(self, request):
        form = InstituteCreationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                with transaction.atomic():
                    # Create Institute
                    institute = Institute.objects.create(
                        name=data['institute_name'],
                        city=data['city'],
                        address=data['address'],
                        phone_number=data['institute_phone_number'],
                        trial_ends_on=timezone.now().date() + timedelta(days=30)
                    )
                    
                    # Generate or use password
                    raw_password = data['password'] or get_random_string(length=8)
                    
                    # Create Owner
                    owner = CustomUser.objects.create_user(
                        phone_number=data['owner_phone_number'],
                        password=raw_password,
                        first_name=data['owner_name'],
                        role='owner',
                        institute=institute
                    )
                    
                    log_activity(request.user, f"Created institute: {institute.name} with owner: {owner.get_full_name()}", institute)
                    
                    # Render confirmation screen (passing password just once)
                    return render(request, 'platform_admin/institute_created.html', {
                        'institute': institute,
                        'owner': owner,
                        'password': raw_password
                    })
            except Exception as e:
                messages.error(request, f"Error creating institute: {str(e)}")
        
        return render(request, 'platform_admin/institute_form.html', {'form': form})
