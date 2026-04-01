from datetime import date
from decimal import Decimal
from django.db.models import Sum, Count
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Ledger, Section, Expense, Category
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import UserSettings
from django.shortcuts import redirect


@login_required
def budget_dashboard(request):
    # Pobieramy wszystkie dziedziny zalogowanego użytkownika
    ledgers = Ledger.objects.filter(user=request.user).order_by('sort_order', '-created_at')
    pinned_sections = Section.objects.filter(ledger__user=request.user, is_pinned=True)
    categories = Category.objects.filter(user=request.user)
    return render(request, 'budget/dashboard.html',
                  {'ledgers': ledgers, 'categories': categories, 'pinned_sections': pinned_sections, })


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

    category_data = expenses.values(
        'category__name',
        'category__color'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')  # Sortujemy od największych wydatków

    chart_labels = []
    chart_values = []
    chart_colors = []

    for entry in category_data:
        # Obsługa wydatków bez kategorii (jeśli takie są)
        name = entry['category__name'] or "Bez kategorii"
        color = entry['category__color'] or "#6c757d"  # Domyślny szary

        chart_labels.append(name)
        # Zamieniamy Decimal na float, bo JS nie lubi Decimal
        chart_values.append(float(entry['total']))
        chart_colors.append(color)

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
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'chart_colors': chart_colors,
        # Przekazujemy też pogrupowane dane, żeby zrobić legendę w HTML
        'category_stats': category_data,
    }
    return render(request, 'budget/section_detail.html', context)


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    section_pk = expense.section.pk
    if request.method == 'POST':
        expense.delete()
    return redirect('budget:section_detail', pk=section_pk)


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
def delete_section(request, pk):
    section = get_object_or_404(Section, pk=pk, ledger__user=request.user)
    if request.method == 'POST':
        section.delete()
    return redirect('budget:budget_dashboard')


@login_required
def delete_ledger(request, pk):
    ledger = get_object_or_404(Ledger, pk=pk, user=request.user)

    # Sprawdzamy, czy dziedzina jest pusta
    if ledger.sections.count() == 0:
        if request.method == 'POST':
            ledger.delete()
            return redirect('budget:budget_dashboard')
    else:
        # Opcjonalnie: komunikat o błędzie, jeśli ktoś próbuje obejść UI
        from django.contrib import messages
        messages.error(request, "Nie można usunąć dziedziny, która zawiera sekcje!")

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


@login_required
def ledger_detail(request, pk):
    ledger = get_object_or_404(Ledger, pk=pk, user=request.user)

    # Pobieramy WSZYSTKIE wydatki dla tej dziedziny (ze wszystkich jej sekcji)
    expenses = Expense.objects.filter(section__ledger=ledger)

    # Suma całkowita wydatków w dziedzinie
    total_amount = expenses.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Opcjonalnie: Suma całkowitego budżetu ze wszystkich sekcji
    total_budget_account = ledger.sections.aggregate(Sum('budget_account'))['budget_account__sum'] or Decimal('0.00')
    stats = ledger.sections.aggregate(
        total_income=Sum('income'),
        sections_count=Count('id')
    )

    # Wyciągamy wartości (z zabezpieczeniem przed None)
    total_income = stats['total_income'] or Decimal('0.00')
    sections_count = stats['sections_count'] or 0
    if sections_count > 0:
        total_income_per_section = Decimal(total_income / sections_count)
    else:
        total_income_per_section = 0
    total_budget_cash = ledger.sections.aggregate(Sum('budget_cash'))['budget_cash__sum'] or Decimal('0.00')
    total_budget = total_budget_account + total_budget_cash

    # DANE DO WYKRESU (Grupowanie po kategoriach dla całej dziedziny)
    category_data = expenses.values(
        'category__name',
        'category__color'
    ).annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')

    chart_labels = []
    chart_values = []
    chart_colors = []

    # Przygotowujemy listy dla Chart.js i liczymy procenty
    for entry in category_data:
        name = entry['category__name'] or "Bez kategorii"
        color = entry['category__color'] or "#6c757d"
        total_val = float(entry['total'])

        # Obliczanie procentu w widoku (bezpieczne, bez mathfilters!)
        percentage = (total_val / float(total_amount) * 100) if total_amount > 0 else 0
        entry['percentage'] = percentage

        chart_labels.append(name)
        chart_values.append(total_val)
        chart_colors.append(color)

    expenses_by_category = defaultdict(list)
    expenses = Expense.objects.filter(
        section__ledger=ledger
    ).select_related('category').order_by('-date')

    # Grupowanie danych w Pythonie
    grouped_data = {}
    for exp in expenses:
        cat = exp.category
        if cat not in grouped_data:
            grouped_data[cat] = {
                'category': cat,
                'expenses': [],
                'total': 0
            }
        grouped_data[cat]['expenses'].append(exp)
        grouped_data[cat]['total'] += exp.amount
    sorted_categories = sorted(
        grouped_data.values(),
        key=lambda x: x['total'],
        reverse=True
    )

    context = {
        'ledger': ledger,
        'expenses_by_category': sorted_categories,
        'total_amount_expenses': sum(item['total'] for item in grouped_data.values()),
        'total_amount': total_amount,
        'total_budget': total_budget,
        'total_budget_cash': total_budget_cash,
        'total_income': total_income,
        'total_income_per_section': total_income_per_section,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'chart_colors': chart_colors,
        'category_stats': category_data,
    }
    return render(request, 'budget/ledger_detail.html', context)


@require_POST
def toggle_income_setting(request):
    # Pobieramy ustawienia (tworzymy je, jeśli nie istnieją)
    settings, created = UserSettings.objects.get_or_create(user=request.user)
    settings.hide_income = not settings.hide_income
    settings.save()
    return JsonResponse({'hide_income': settings.hide_income})


def move_ledger(request, ledger_id, direction):
    ledger = get_object_or_404(Ledger, id=ledger_id, user=request.user)

    # Szukamy sąsiada w zależności od kierunku
    if direction == 'up':
        # Sąsiad "wyżej" to ten z mniejszym sort_order (ale najbliższy)
        neighbor = Ledger.objects.filter(
            user=request.user,
            sort_order__lt=ledger.sort_order
        ).order_by('-sort_order').first()
    else:
        # Sąsiad "niżej" to ten z większym sort_order (ale najbliższy)
        neighbor = Ledger.objects.filter(
            user=request.user,
            sort_order__gt=ledger.sort_order
        ).order_by('sort_order').first()

    if neighbor:
        # Klasyczna zamiana wartości (swap)
        old_order = ledger.sort_order
        ledger.sort_order = neighbor.sort_order
        neighbor.sort_order = old_order

        ledger.save()
        neighbor.save()

    return redirect('budget:budget_dashboard')


def toggle_pin_section(request, section_id):
    section = get_object_or_404(Section, id=section_id, ledger__user=request.user)
    section.is_pinned = not section.is_pinned
    section.save()
    # Przeładowanie strony (nasz AJAX przechwyci i tak tylko HTML)
    return redirect('budget:budget_dashboard')
