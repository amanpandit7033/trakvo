from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from apps.core.mixins import OwnerRequiredMixin
from .models import Institute, Batch
from .forms import InstituteForm, BatchForm

class InstituteProfileView(OwnerRequiredMixin, UpdateView):
    model = Institute
    form_class = InstituteForm
    template_name = 'institutes/profile.html'
    success_url = reverse_lazy('institutes:profile')

    def get_object(self, queryset=None):
        return self.request.user.institute

class BatchListView(OwnerRequiredMixin, ListView):
    model = Batch
    template_name = 'institutes/batch_list.html'
    context_object_name = 'batches'

    def get_queryset(self):
        if self.request.user.institute:
            return Batch.objects.filter(institute=self.request.user.institute)
        return Batch.objects.none()

class BatchCreateView(OwnerRequiredMixin, CreateView):
    model = Batch
    form_class = BatchForm
    template_name = 'institutes/batch_form.html'
    success_url = reverse_lazy('institutes:batch_list')

    def form_valid(self, form):
        form.instance.institute = self.request.user.institute
        return super().form_valid(form)

class BatchUpdateView(OwnerRequiredMixin, UpdateView):
    model = Batch
    form_class = BatchForm
    template_name = 'institutes/batch_form.html'
    success_url = reverse_lazy('institutes:batch_list')

    def get_queryset(self):
        if self.request.user.institute:
            return Batch.objects.filter(institute=self.request.user.institute)
        return Batch.objects.none()

class BatchDeleteView(OwnerRequiredMixin, DeleteView):
    model = Batch
    template_name = 'institutes/batch_confirm_delete.html'
    success_url = reverse_lazy('institutes:batch_list')

    def get_queryset(self):
        if self.request.user.institute:
            return Batch.objects.filter(institute=self.request.user.institute)
        return Batch.objects.none()
