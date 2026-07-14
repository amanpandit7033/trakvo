from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Prefetch

from apps.core.mixins import OwnerRequiredMixin
from apps.students.models import Student
from .models import FeeStructure, Payment
from .forms import FeeStructureForm, PaymentForm
import xhtml2pdf.pisa as pisa
from io import BytesIO

class FeeListView(LoginRequiredMixin, ListView):
    model = FeeStructure
    template_name = 'fees/fee_list.html'
    context_object_name = 'fee_structures'

    def get_queryset(self):
        institute = self.request.user.institute
        if not institute:
            return FeeStructure.objects.none()
        
        queryset = FeeStructure.objects.filter(student__institute=institute, student__is_active=True).select_related('student', 'student__batch').prefetch_related('payments').order_by('due_date')
        
        status_filter = self.request.GET.get('status')
        if status_filter:
            # We filter in Python because the status is a property
            if status_filter == 'paid':
                queryset = [fs for fs in queryset if fs.status == 'paid']
            elif status_filter == 'partial':
                queryset = [fs for fs in queryset if fs.status == 'partial']
            elif status_filter == 'pending':
                queryset = [fs for fs in queryset if fs.status == 'pending']
                
        return queryset

class FeeStructureCreateView(OwnerRequiredMixin, CreateView):
    model = FeeStructure
    form_class = FeeStructureForm
    template_name = 'fees/fee_structure_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = get_object_or_404(Student, pk=self.kwargs['student_id'], institute=self.request.user.institute)
        return context

    def form_valid(self, form):
        student = get_object_or_404(Student, pk=self.kwargs['student_id'], institute=self.request.user.institute)
        form.instance.student = student
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('students:student_detail', kwargs={'pk': self.kwargs['student_id']})

class PaymentRecordView(OwnerRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'fees/payment_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fee_structure = get_object_or_404(FeeStructure, pk=self.kwargs['fee_structure_id'], student__institute=self.request.user.institute)
        context['fee_structure'] = fee_structure
        return context

    def form_valid(self, form):
        fee_structure = get_object_or_404(FeeStructure, pk=self.kwargs['fee_structure_id'], student__institute=self.request.user.institute)
        form.instance.fee_structure = fee_structure
        form.instance.recorded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('students:student_detail', kwargs={'pk': self.object.fee_structure.student.id})

class FeeReceiptView(LoginRequiredMixin, View):
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, pk=payment_id, fee_structure__student__institute=request.user.institute)
        template_path = 'fees/receipt_pdf.html'
        context = {'payment': payment, 'institute': request.user.institute}
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.pdf"'
        
        template = get_template(template_path)
        html = template.render(context)
        
        pisa_status = pisa.CreatePDF(
            html, dest=response
        )
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
