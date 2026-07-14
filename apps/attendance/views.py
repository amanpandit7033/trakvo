from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime

from apps.institutes.models import Batch
from apps.students.models import Student
from .models import AttendanceRecord

class AttendanceMarkView(LoginRequiredMixin, View):
    template_name = 'attendance/mark_attendance.html'

    def get(self, request, batch_id=None, date_str=None):
        institute = request.user.institute
        if not institute:
            return redirect('institutes:profile')

        batches = Batch.objects.filter(institute=institute)
        
        # Determine selected date and batch
        selected_date = timezone.now().date()
        if date_str:
            try:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                pass
        
        selected_batch = None
        students = []
        attendance_map = {}

        if batch_id:
            selected_batch = get_object_or_404(Batch, pk=batch_id, institute=institute)
            students = Student.objects.filter(batch=selected_batch, is_active=True).order_by('full_name')
            
            # Fetch existing records
            existing_records = AttendanceRecord.objects.filter(batch=selected_batch, date=selected_date)
            for record in existing_records:
                attendance_map[record.student_id] = record.status

        # Add existing status to student objects for the template
        for student in students:
            student.current_status = attendance_map.get(student.id, None)

        context = {
            'batches': batches,
            'selected_batch': selected_batch,
            'selected_date': selected_date.isoformat(),
            'students': students,
        }
        return render(request, self.template_name, context)

    def post(self, request, batch_id=None, date_str=None):
        institute = request.user.institute
        
        batch_id = request.POST.get('batch_id')
        date_str = request.POST.get('date')
        
        if not batch_id or not date_str:
            return redirect('attendance:mark_attendance')
            
        selected_batch = get_object_or_404(Batch, pk=batch_id, institute=institute)
        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = timezone.now().date()
            
        if selected_date > timezone.now().date():
            # Basic validation check - could add messages framework error here
            return redirect('attendance:mark_attendance_specific', batch_id=batch_id, date_str=date_str)

        students = Student.objects.filter(batch=selected_batch, is_active=True)
        
        # Validation: Check if all students have a status selected
        missing_attendance = False
        for student in students:
            if not request.POST.get(f'status_{student.id}'):
                missing_attendance = True
                break
                
        if missing_attendance:
            from django.contrib import messages
            messages.error(request, 'Mark attendance for all students before saving.')
            return redirect('attendance:mark_attendance_specific', batch_id=batch_id, date_str=date_str)
        
        # Bulk save logic
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            if status in ['present', 'absent']:
                AttendanceRecord.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={
                        'batch': selected_batch,
                        'status': status,
                        'marked_by': request.user
                    }
                )
                
        return redirect('attendance:mark_attendance_specific', batch_id=batch_id, date_str=selected_date.isoformat())

class AttendanceSummaryView(LoginRequiredMixin, View):
    def get(self, request, student_id):
        student = get_object_or_404(Student, pk=student_id, institute=request.user.institute)
        
        records = AttendanceRecord.objects.filter(student=student)
        total_days = records.count()
        present_days = records.filter(status='present').count()
        
        percentage = 0
        if total_days > 0:
            percentage = round((present_days / total_days) * 100)
            
        recent_absences = records.filter(status='absent').order_by('-date')[:5]
        
        context = {
            'student': student,
            'attendance_percentage': percentage,
            'recent_absences': recent_absences,
            'total_days': total_days
        }
        return render(request, 'attendance/summary_partial.html', context)
