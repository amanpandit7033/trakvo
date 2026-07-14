from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import OwnerRequiredMixin
from .models import Student
from apps.institutes.models import Batch
from .forms import StudentForm
from django.template.response import TemplateResponse

class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        institute = self.request.user.institute
        if not institute:
            return Student.objects.none()
        
        queryset = Student.objects.filter(institute=institute, is_active=True)
        
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) | 
                Q(parent_phone_number__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
            
        batch_id = self.request.GET.get('batch', '')
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.institute:
            context['batches'] = Batch.objects.filter(institute=self.request.user.institute)
            
            from apps.fees.models import FeeStructure
            from django.utils import timezone
            today = timezone.now().date()
            
            students = context['students']
            fee_structures = FeeStructure.objects.filter(student__in=students).prefetch_related('payments')
            
            student_fees = {}
            for fs in fee_structures:
                student_fees.setdefault(fs.student_id, []).append(fs)
                
            for student in students:
                fees = student_fees.get(student.id, [])
                if not fees:
                    student.fee_status_label = "Not set"
                else:
                    total_balance = sum(f.balance_due for f in fees)
                    total_paid = sum(f.total_paid for f in fees)
                    
                    if total_balance <= 0:
                        student.fee_status_label = "Paid"
                    else:
                        is_overdue = any(f.balance_due > 0 and f.due_date < today for f in fees)
                        if is_overdue:
                            student.fee_status_label = "Overdue"
                        elif total_paid > 0:
                            student.fee_status_label = "Partial"
                        else:
                            student.fee_status_label = "Pending"
                            
        return context

class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def get_queryset(self):
        institute = self.request.user.institute
        if not institute:
            return Student.objects.none()
        return Student.objects.filter(institute=institute)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.attendance.models import AttendanceRecord
        records = AttendanceRecord.objects.filter(student=self.object)
        total_days = records.count()
        present_days = records.filter(status='present').count()
        percentage = 0
        if total_days > 0:
            percentage = round((present_days / total_days) * 100)
        recent_absences = records.filter(status='absent').order_by('-date')[:5]
        
        context['attendance_percentage'] = percentage
        context['total_days'] = total_days
        context['recent_absences'] = recent_absences
        
        from apps.fees.models import FeeStructure
        fee_structures = FeeStructure.objects.filter(student=self.object).prefetch_related('payments').order_by('-due_date')
        context['fee_structures'] = fee_structures
        
        from apps.assessments.models import TestResult
        from apps.assessments.services import calculate_ranks
        results = TestResult.objects.filter(student=self.object).select_related('test').order_by('-test__test_date')[:5]
        history = []
        for result in results:
            test_ranks = calculate_ranks(result.test)
            rank = next((r['rank'] for r in test_ranks if r['student'] == self.object), None)
            history.append({
                'test': result.test,
                'marks': result.marks_obtained,
                'rank': rank
            })
        context['history'] = history
        
        return context

class StudentCreateView(OwnerRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['institute'] = self.request.user.institute
        return kwargs

    def form_valid(self, form):
        form.instance.institute = self.request.user.institute
        return super().form_valid(form)

class StudentUpdateView(OwnerRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def get_queryset(self):
        institute = self.request.user.institute
        if not institute:
            return Student.objects.none()
        return Student.objects.filter(institute=institute)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['institute'] = self.request.user.institute
        return kwargs

class StudentDeactivateView(OwnerRequiredMixin, View):
    def get(self, request, pk):
        student = get_object_or_404(Student, pk=pk, institute=request.user.institute)
        return TemplateResponse(request, 'students/student_confirm_deactivate.html', {'object': student})

    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk, institute=request.user.institute)
        student.is_active = False
        student.save()
        return redirect('students:student_list')
