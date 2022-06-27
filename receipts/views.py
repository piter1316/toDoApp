from django.shortcuts import render
from receipts.models import Receipt


def receipts_home(request):
    user_receipts = Receipt.objects.select_related('category').filter(user=request.user)
    context = {
        'user_receipts': user_receipts}
    return render(request, 'receipts/home.html', context)
