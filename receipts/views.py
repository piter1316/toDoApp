from django.shortcuts import render, redirect
from receipts.models import Receipt
from receipts.forms import ReceiptForm
from django.views.generic import UpdateView, CreateView, DeleteView
from django.urls import reverse, reverse_lazy


def receipts_home(request):
    user_receipts = Receipt.objects.select_related('category').filter(user=request.user).order_by('-purchase_date')
    form = ReceiptForm()
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
        form.instance.user_id = self.request.user.id
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

    def get_success_url(self):
        return '{}'.format(reverse('receipts:receipts_home'))


def receipt_delete(request, pk):
    receipt_to_delete = Receipt.objects.filter(pk=pk).delete()
    return redirect('receipts:receipts_home')
