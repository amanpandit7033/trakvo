from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.core.mixins import OwnerRequiredMixin
from apps.students.models import Student
from .models import Test, TestResult
from .forms import TestForm
from .services import calculate_ranks
from decimal import Decimal, InvalidOperation

class TestListView(LoginRequiredMixin, ListView):
    model = Test
    template_name = 'assessments/test_list.html'
    context_object_name = 'tests'

    def get_queryset(self):
        institute = self.request.user.institute
        if not institute:
            return Test.objects.none()
        return Test.objects.filter(batch__institute=institute).select_related('batch', 'created_by').order_by('-test_date')

class TestCreateView(LoginRequiredMixin, CreateView):
    # Both Owner and Teacher can create tests
    model = Test
    form_class = TestForm
    template_name = 'assessments/test_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['institute'] = self.request.user.institute
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('assessments:marks_entry', kwargs={'test_id': self.object.id})

class TestMarksEntryView(LoginRequiredMixin, View):
    def get(self, request, test_id):
        test = get_object_or_404(Test, id=test_id, batch__institute=request.user.institute)
        students = Student.objects.filter(batch=test.batch, is_active=True).order_by('full_name')
        
        # Pre-fill existing results
        existing_results = {result.student_id: result.marks_obtained for result in TestResult.objects.filter(test=test)}
        
        student_data = []
        for student in students:
            student_data.append({
                'student': student,
                'marks': existing_results.get(student.id, '')
            })
            
        context = {
            'test': test,
            'student_data': student_data
        }
        return render(request, 'assessments/marks_entry.html', context)

    def post(self, request, test_id):
        test = get_object_or_404(Test, id=test_id, batch__institute=request.user.institute)
        students = Student.objects.filter(batch=test.batch, is_active=True)
        
        for student in students:
            marks_str = request.POST.get(f'marks_{student.id}')
            if marks_str and marks_str.strip():
                try:
                    marks = Decimal(marks_str)
                    TestResult.objects.update_or_create(
                        test=test,
                        student=student,
                        defaults={'marks_obtained': marks}
                    )
                except InvalidOperation:
                    pass # Ignore invalid decimals
            else:
                # If cleared out, we could delete it, or leave it. Let's delete if empty.
                TestResult.objects.filter(test=test, student=student).delete()

        messages.success(request, 'Marks saved successfully.')
        return redirect('assessments:test_results', test_id=test.id)

class TestResultsView(LoginRequiredMixin, View):
    def get(self, request, test_id):
        test = get_object_or_404(Test, id=test_id, batch__institute=request.user.institute)
        ranked_results = calculate_ranks(test)
        
        context = {
            'test': test,
            'ranked_results': ranked_results
        }
        return render(request, 'assessments/test_results.html', context)

class StudentTestHistoryView(LoginRequiredMixin, View):
    def get(self, request, student_id):
        student = get_object_or_404(Student, id=student_id, institute=request.user.institute)
        
        # Get all tests the student participated in
        results = TestResult.objects.filter(student=student).select_related('test').order_by('-test__test_date')
        
        # Calculate rank for each test
        history = []
        for result in results:
            test_ranks = calculate_ranks(result.test)
            rank = next((r['rank'] for r in test_ranks if r['student'] == student), None)
            history.append({
                'test': result.test,
                'marks': result.marks_obtained,
                'rank': rank
            })
            
        context = {
            'student': student,
            'history': history
        }
        return render(request, 'assessments/student_test_history.html', context)
