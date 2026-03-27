from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Ledger, Section, Expense, Category


@login_required
def budget_dashboard(request):
    # Pobieramy wszystkie dziedziny zalogowanego użytkownika
    ledgers = Ledger.objects.filter(user=request.user).prefetch_related('sections')
    return render(request, 'budget/dashboard.html', {'ledgers': ledgers})


@login_required
def section_detail(request, pk):
    section = get_object_or_404(Section, pk=pk, ledger__user=request.user)
    categories = Category.objects.filter(user=request.user)

    # Obsługa dodawania nowego wydatku
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        category_id = request.POST.get('category')

        if title and amount and date and category_id:
            category = get_object_or_404(Category, id=category_id, user=request.user)
            Expense.objects.create(
                title=title, amount=amount, date=date,
                category=category, section=section, user=request.user
            )
            return redirect('budget:section_detail', pk=section.pk)

    # Pobieramy wydatki z tej sekcji
    expenses = section.expenses.all().order_by('-date', '-id')
    # Szybka suma wydatków na poziomie bazy danych
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or 0.00

    context = {
        'section': section,
        'expenses': expenses,
        'total_amount': total_amount,
        'categories': categories
    }
    return render(request, 'budget/section_detail.html', context)


@login_required
def add_ledger(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Ledger.objects.create(name=name, user=request.user)
    return redirect('budget:budget_dashboard')


@login_required
def add_section(request, ledger_id):
    ledger = get_object_or_404(Ledger, id=ledger_id, user=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            # Obliczamy kolejność (order) na podstawie ilości istniejących sekcji
            order = ledger.sections.count() + 1
            Section.objects.create(name=name, ledger=ledger, order=order)
    return redirect('budget:budget_dashboard')


@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color', '#316C9A')
        if name:
            Category.objects.create(name=name, color=color, user=request.user)
    # Wracamy tam, skąd przyszliśmy
    return redirect(request.META.get('HTTP_REFERER', 'budget:budget_dashboard'))
