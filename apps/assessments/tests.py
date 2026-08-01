from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
import uuid
from apps.institutes.models import Institute, Batch
from apps.accounts.models import CustomUser
from apps.students.models import Student
from apps.assessments.models import Test, TestResult

class ScoreboardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Institute A setup
        self.inst_a = Institute.objects.create(name="Apex Academy", city="Patna", phone_number="9998887771")
        self.batch_a = Batch.objects.create(institute=self.inst_a, name="Class 10")
        self.student_a1 = Student.objects.create(institute=self.inst_a, batch=self.batch_a, full_name="Rahul Kumar", parent_name="Sanjay", parent_phone_number="9900000001")
        self.student_a2 = Student.objects.create(institute=self.inst_a, batch=self.batch_a, full_name="Anita Roy", parent_name="Vikram", parent_phone_number="9900000002")
        self.test_a = Test.objects.create(batch=self.batch_a, name="Physics Midterm", test_date="2026-08-01", max_marks=Decimal('100.00'))
        TestResult.objects.create(test=self.test_a, student=self.student_a1, marks_obtained=Decimal('95.00'))
        TestResult.objects.create(test=self.test_a, student=self.student_a2, marks_obtained=Decimal('88.00'))
        
        self.owner_a = CustomUser.objects.create_user(phone_number="1111111111", password="password123", role="owner", institute=self.inst_a)

        # Institute B setup
        self.inst_b = Institute.objects.create(name="Brilliant Tutorials", city="Gaya", phone_number="9998887772")
        self.batch_b = Batch.objects.create(institute=self.inst_b, name="Class 12")
        self.student_b1 = Student.objects.create(institute=self.inst_b, batch=self.batch_b, full_name="Sunil Sharma", parent_name="Ramesh", parent_phone_number="9900000003")
        self.owner_b = CustomUser.objects.create_user(phone_number="2222222222", password="password123", role="owner", institute=self.inst_b)

    def test_scoreboard_access_by_valid_token(self):
        url = reverse('assessments:institute_scoreboard', kwargs={'token': self.inst_a.access_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apex Academy")
        self.assertContains(response, "Rahul Kumar")
        self.assertContains(response, "95")
        # Ensure Institute B data is NOT present
        self.assertNotContains(response, "Brilliant Tutorials")
        self.assertNotContains(response, "Sunil Sharma")

    def test_scoreboard_invalid_token(self):
        url = reverse('assessments:institute_scoreboard', kwargs={'token': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_scoreboard_cross_tenant_isolation_logged_in(self):
        # Log in as Owner A
        self.client.login(username="1111111111", password="password123")
        # Attempt to access Institute B's token URL
        url_b = reverse('assessments:institute_scoreboard', kwargs={'token': self.inst_b.access_token})
        response = self.client.get(url_b)
        # Redirects back to /assessments/scoreboard/
        self.assertRedirects(response, reverse('assessments:scoreboard'), target_status_code=302)

    def test_scoreboard_suspended_institute(self):
        self.inst_a.is_suspended = True
        self.inst_a.save()
        url = reverse('assessments:institute_scoreboard', kwargs={'token': self.inst_a.access_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Scoreboard Unavailable", status_code=403)
