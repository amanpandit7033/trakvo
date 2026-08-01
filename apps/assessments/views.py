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

from apps.institutes.models import Institute, Batch

class InstituteScoreboardView(View):
    def get(self, request, token):
        # Fetch institute by unguessable access_token
        institute = get_object_or_404(Institute, access_token=token)

        # Security check 1: Enforce suspended status check
        if institute.is_suspended:
            return render(request, 'assessments/scoreboard_suspended.html', {'institute': institute}, status=403)

        # Security check 2: Prevent authenticated users from another institute from accessing
        if request.user.is_authenticated and request.user.role in ['owner', 'teacher']:
            if request.user.institute and request.user.institute != institute:
                messages.error(request, "You can only access your own institute's scoreboard.")
                return redirect('assessments:scoreboard')

        batches = Batch.objects.filter(institute=institute).order_by('name')

        # Batch filter
        selected_batch_id = request.GET.get('batch')
        selected_batch = None
        if selected_batch_id:
            try:
                selected_batch = batches.get(id=int(selected_batch_id))
            except (ValueError, Batch.DoesNotExist):
                selected_batch = None

        # Filter tests by institute (and batch if selected)
        tests_qs = Test.objects.filter(batch__institute=institute).select_related('batch').order_by('-test_date', '-created_at')
        if selected_batch:
            tests_qs = tests_qs.filter(batch=selected_batch)

        tests = list(tests_qs)

        # Selected test
        test_id_param = request.GET.get('test')
        selected_test = None

        if test_id_param:
            try:
                test_id = int(test_id_param)
                selected_test = next((t for t in tests if t.id == test_id), None)
                if not selected_test:
                    # Fallback check directly in DB scoped strictly to institute
                    selected_test = Test.objects.filter(id=test_id, batch__institute=institute).first()
            except ValueError:
                pass

        if not selected_test and tests:
            selected_test = tests[0]

        ranked_results = []
        top_3 = []

        if selected_test:
            ranked_results = calculate_ranks(selected_test)
            for item in ranked_results:
                max_m = item['max_marks']
                if max_m and max_m > 0:
                    item['percentage'] = round((item['marks'] / max_m) * 100, 1)
                else:
                    item['percentage'] = 0.0
            top_3 = ranked_results[:3]

        total_students = Student.objects.filter(institute=institute, is_active=True).count()
        is_staff = request.user.is_authenticated and request.user.institute == institute and request.user.role in ['owner', 'teacher']

        scoreboard_url = request.build_absolute_uri()

        context = {
            'institute': institute,
            'batches': batches,
            'selected_batch': selected_batch,
            'tests': tests,
            'selected_test': selected_test,
            'ranked_results': ranked_results,
            'top_3': top_3,
            'total_students': total_students,
            'is_staff': is_staff,
            'scoreboard_url': scoreboard_url,
        }
        return render(request, 'assessments/scoreboard.html', context)

class OwnerTeacherScoreboardRedirectView(LoginRequiredMixin, View):
    def get(self, request):
        institute = request.user.institute
        if not institute:
            messages.error(request, "No institute assigned to your account.")
            return redirect('accounts:login')
        return redirect('assessments:institute_scoreboard', token=institute.access_token)

