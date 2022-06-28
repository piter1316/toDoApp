from django.shortcuts import render, redirect, get_object_or_404
from receipts.models import Receipt
from receipts.forms import ReceiptForm
from django.views.generic import UpdateView, CreateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.core.files.storage import FileSystemStorage
import os
from myproject.settings import BASE_DIR, MEDIA_ROOT
from django.core.files.storage import default_storage

def receipts_home(request):
    user_receipts = Receipt.objects.select_related('category').filter(user=request.user).order_by('-purchase_date')
    form = ReceiptForm(request.POST, request.FILES)
    context = {
        'user_receipts': user_receipts,
        'form': form,
    }
    return render(request, 'receipts/home.html', context)


class ReceiptCreateView(CreateView):
    model = Receipt
    form_class = ReceiptForm
    success_url = 'receipts'

    def form_valid(self, form):
        new_receipt = form.save(commit=False)
        location = os.path.join(BASE_DIR, 'media', 'user_uploads',
                                '{}-{}'.format(self.request.user.id, self.request.user.username), 'receipts', str(new_receipt.file))
        location_to_database = os.path.join('media', 'user_uploads',
                                            '{}-{}'.format(self.request.user.id, self.request.user.username), 'receipts')
        fs = FileSystemStorage(location=location)
        file = self.request.FILES.get('file', False)
        fs.save(str(file), file)
        form.instance.user_id = self.request.user.id
        form.instance.file = os.path.join(location_to_database, str(file))
        return super().form_valid(form)


class ReceiptEdit(UpdateView):
    model = Receipt
    form_class = ReceiptForm
    template_name = 'receipts/receipt.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     pk = self.object.pk
    #     context['receipt'] = Receipt.objects.select_related('category').filter(pk=pk, user=request.user)[0]
    #     return context
    def form_valid(self, form):
        new_receipt = form.save(commit=False)
        location = os.path.join('media', 'user_uploads',
                                '{}-{}'.format(self.request.user.id, self.request.user.username), 'receipts',)
        location_to_database = os.path.join('media', 'user_uploads',
                                            '{}-{}'.format(self.request.user.id, self.request.user.username), 'receipts')
        fs = FileSystemStorage(location=location)
        file = self.request.FILES.get('file', False)
        current_receipt_object = get_object_or_404(Receipt, pk=form.instance.id)
        if current_receipt_object.file:
            default_storage.delete(os.path.join(BASE_DIR,str(current_receipt_object.file)))
        fs.save(str(file), file)
        form.instance.user_id = self.request.user.id
        form.instance.file = os.path.join(location, str(file))
        return super().form_valid(form)

    def get_success_url(self):
        return '{}'.format(reverse('receipts:receipts_home'))


def receipt_delete(request, pk):
    receipt_to_delete = Receipt.objects.filter(pk=pk).delete()
    return redirect('receipts:receipts_home')
