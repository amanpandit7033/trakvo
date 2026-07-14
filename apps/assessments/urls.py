from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    path('', views.TestListView.as_view(), name='test_list'),
    path('add/', views.TestCreateView.as_view(), name='test_add'),
    path('<int:test_id>/marks/', views.TestMarksEntryView.as_view(), name='marks_entry'),
    path('<int:test_id>/results/', views.TestResultsView.as_view(), name='test_results'),
    path('student/<int:student_id>/history/', views.StudentTestHistoryView.as_view(), name='student_history'),
]
