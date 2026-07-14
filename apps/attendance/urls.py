from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('mark/', views.AttendanceMarkView.as_view(), name='mark_attendance'),
    path('mark/<int:batch_id>/<str:date_str>/', views.AttendanceMarkView.as_view(), name='mark_attendance_specific'),
    path('summary/<int:student_id>/', views.AttendanceSummaryView.as_view(), name='summary'),
]
