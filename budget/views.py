from datetime import date
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Ledger, Section, Expense, Category


@login_required
def budget_dashboard(request):
    # Pobieramy wszystkie dziedziny zalogowanego użytkownika
    ledgers = Ledger.objects.filter(user=request.user).prefetch_related('sections')
    categories = Category.objects.filter(user=request.user)
    print(categories)
    return render(request, 'budget/dashboard.html', {'ledgers': ledgers, 'categories': categories})


@login_required
def section_detail(request, pk):
    section = get_object_or_404(Section, pk=pk, ledger__user=request.user)
    categories = Category.objects.filter(user=request.user)

    # Obsługa dodawania wydatku
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        expense_date = request.POST.get('date')
        category_id = request.POST.get('category')
        is_cash = request.POST.get('is_cash') == 'on'

        if title and amount and expense_date:
            if category_id:
                category = get_object_or_404(Category, id=category_id, user=request.user)
            else:
                category = None
            Expense.objects.create(
                title=title, amount=amount, date=expense_date,
                category=category, section=section, user=request.user,
                is_cash=is_cash
            )
            return redirect('budget:section_detail', pk=section.pk)

    # Obliczenia do widoku
    expenses = section.expenses.all().order_by('-date', '-id')

    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    cash_expenses = expenses.filter(is_cash=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    account_expenses = expenses.filter(is_cash=False).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    total_budget = section.budget_account + section.budget_cash

    context = {
        'section': section,
        'expenses': expenses,
        'categories': categories,
        'today': date.today(),  # Przekazujemy dzisiejszą datę

        # Statystyki
        'total_amount': total_amount,
        'cash_expenses': cash_expenses,
        'account_expenses': account_expenses,
        'total_budget': total_budget,
        'remaining_account': section.budget_account - account_expenses,
        'remaining_cash': section.budget_cash - cash_expenses,
        'remaining_total': total_budget - total_amount,
    }
    return render(request, 'budget/section_detail.html', context)


@login_required
def edit_section_budget(request, pk):
    section = get_object_or_404(Section, pk=pk, ledger__user=request.user)
    if request.method == 'POST':
        section.income = request.POST.get('income', 0)
        section.budget_account = request.POST.get('budget_account', 0)
        section.budget_cash = request.POST.get('budget_cash', 0)
        section.save()
    return redirect('budget:section_detail', pk=section.pk)


@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.color = request.POST.get('color')
        category.save()
    return redirect(request.META.get('HTTP_REFERER', 'budget:budget_dashboard'))


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
