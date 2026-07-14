from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, View
from django.template.response import TemplateResponse
from apps.core.mixins import OwnerRequiredMixin, TeacherRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal

from apps.students.models import Student
from apps.institutes.models import Batch
from apps.attendance.models import AttendanceRecord
from apps.fees.models import FeeStructure, Payment
from apps.assessments.models import Test, TestResult
from .models import CustomUser
from .forms import TeacherCreationForm

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        user = form.get_user()
        if user.role in ['owner', 'teacher'] and user.institute:
            from django.contrib import messages
            from django.utils import timezone
            
            if user.institute.is_suspended:
                messages.error(self.request, "Your institute's access has been suspended. Contact support.")
                return self.render_to_response(self.get_context_data(form=form))
                
            if user.institute.trial_ends_on and user.institute.trial_ends_on < timezone.now().date():
                messages.error(self.request, "Your institute's trial has expired. Please contact support to renew.")
                return self.render_to_response(self.get_context_data(form=form))
                
        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        if user.role == 'super_admin':
            return reverse_lazy('platform_admin:dashboard')
        elif user.role == 'owner':
            return reverse_lazy('accounts:owner_dashboard')
        elif user.role == 'teacher':
            return reverse_lazy('accounts:teacher_dashboard')
        return reverse_lazy('accounts:login')

class OwnerDashboardView(OwnerRequiredMixin, TemplateView):
    template_name = 'accounts/owner_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        institute = self.request.user.institute
        today = timezone.now().date()
        
        if not institute:
            return context

        # 1. Quick Stats
        active_students_count = Student.objects.filter(institute=institute, is_active=True).count()
        total_batches_count = Batch.objects.filter(institute=institute).count()
        
        start_of_month = today.replace(day=1)
        this_month_payments = Payment.objects.filter(
            fee_structure__student__institute=institute,
            payment_date__gte=start_of_month
        ).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')

        # 2. Attendance Snapshot
        batches_with_attendance_today = AttendanceRecord.objects.filter(
            student__institute=institute, 
            date=today
        ).values_list('batch_id', flat=True).distinct()
        
        batches_pending_attendance = Batch.objects.filter(
            institute=institute
        ).exclude(id__in=batches_with_attendance_today)
        
        total_marked_today = AttendanceRecord.objects.filter(student__institute=institute, date=today)
        total_marked_count = total_marked_today.count()
        present_count = total_marked_today.filter(status='present').count()
        attendance_percent = (present_count / total_marked_count * 100) if total_marked_count > 0 else 0

        # 3. Fees Snapshot
        all_fees = FeeStructure.objects.filter(student__institute=institute).select_related('student', 'student__batch').prefetch_related('payments')
        
        total_balance = Decimal('0.00')
        overdue_fees = []
        
        for fee in all_fees:
            total_balance += fee.balance_due
            if fee.balance_due > 0 and fee.due_date < today:
                fee.days_overdue = (today - fee.due_date).days
                overdue_fees.append(fee)
                
        students_overdue_count = len(overdue_fees)
        top_5_overdue = sorted(overdue_fees, key=lambda f: f.balance_due, reverse=True)[:5]

        # 4. Recent Tests Snapshot
        recent_tests = Test.objects.filter(batch__institute=institute).select_related('batch').order_by('-created_at')[:3]
        
        test_info = []
        for test in recent_tests:
            active_students_in_batch = Student.objects.filter(batch=test.batch, is_active=True).count()
            results_count = TestResult.objects.filter(test=test).count()
            is_complete = results_count >= active_students_in_batch and active_students_in_batch > 0
            test_info.append({
                'test': test,
                'is_complete': is_complete
            })

        context.update({
            'active_students_count': active_students_count,
            'total_batches_count': total_batches_count,
            'this_month_collection': this_month_payments,
            'batches_pending_attendance': batches_pending_attendance,
            'attendance_percent': round(attendance_percent, 1),
            'total_balance': total_balance,
            'students_overdue_count': students_overdue_count,
            'top_5_overdue': top_5_overdue,
            'recent_tests': test_info,
            'today_str': today.strftime("%Y-%m-%d"),
        })
        return context

class TeacherDashboardView(TeacherRequiredMixin, TemplateView):
    template_name = 'accounts/teacher_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        institute = self.request.user.institute
        today = timezone.now().date()
        
        if not institute:
            return context

        # 1. Quick Stats (Teacher specific)
        active_students_count = Student.objects.filter(institute=institute, is_active=True).count()
        total_batches_count = Batch.objects.filter(institute=institute).count()

        # 2. Attendance Snapshot
        batches_with_attendance_today = AttendanceRecord.objects.filter(
            student__institute=institute, 
            date=today
        ).values_list('batch_id', flat=True).distinct()
        
        batches_pending_attendance = Batch.objects.filter(
            institute=institute
        ).exclude(id__in=batches_with_attendance_today)

        # 3. Recent Tests Snapshot
        recent_tests = Test.objects.filter(batch__institute=institute).select_related('batch').order_by('-created_at')[:3]
        
        test_info = []
        for test in recent_tests:
            active_students_in_batch = Student.objects.filter(batch=test.batch, is_active=True).count()
            results_count = TestResult.objects.filter(test=test).count()
            is_complete = results_count >= active_students_in_batch and active_students_in_batch > 0
            test_info.append({
                'test': test,
                'is_complete': is_complete
            })

        context.update({
            'active_students_count': active_students_count,
            'total_batches_count': total_batches_count,
            'batches_pending_attendance': batches_pending_attendance,
            'recent_tests': test_info,
            'today_str': today.strftime("%Y-%m-%d"),
        })
        return context

class TeacherListView(OwnerRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/teacher_list.html'
    context_object_name = 'teachers'

    def get_queryset(self):
        institute = self.request.user.institute
        if not institute:
            return CustomUser.objects.none()
        return CustomUser.objects.filter(institute=institute, role='teacher', is_active=True)

class TeacherCreateView(OwnerRequiredMixin, CreateView):
    model = CustomUser
    form_class = TeacherCreationForm
    template_name = 'accounts/teacher_form.html'
    success_url = reverse_lazy('accounts:teacher_list')

    def form_valid(self, form):
        form.instance.institute = self.request.user.institute
        form.instance.role = 'teacher'
        return super().form_valid(form)

class TeacherDeactivateView(OwnerRequiredMixin, View):
    def get(self, request, pk):
        teacher = get_object_or_404(CustomUser, pk=pk, institute=request.user.institute, role='teacher')
        return TemplateResponse(request, 'accounts/teacher_confirm_deactivate.html', {'object': teacher})

    def post(self, request, pk):
        teacher = get_object_or_404(CustomUser, pk=pk, institute=request.user.institute, role='teacher')
        teacher.is_active = False
        teacher.save()
        return redirect('accounts:teacher_list')

from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'accounts/change_password.html'
    
    def get_success_url(self):
        user = self.request.user
        from django.contrib import messages
        messages.success(self.request, "Password changed successfully.")
        
        if user.role == 'super_admin':
            return reverse_lazy('platform_admin:dashboard')
        elif user.role == 'owner':
            return reverse_lazy('accounts:owner_dashboard')
        elif user.role == 'teacher':
            return reverse_lazy('accounts:teacher_dashboard')
        return reverse_lazy('accounts:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role == 'super_admin':
            context['base_template'] = 'platform_admin/base_admin.html'
        else:
            context['base_template'] = 'base.html'
        return context
