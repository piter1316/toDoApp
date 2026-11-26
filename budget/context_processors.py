from .models import Section


def pinned_budget_sections(request):
    if not request.user.is_authenticated:
        return {'pinned_budget_sections': Section.objects.none()}

    return {
        'pinned_budget_sections': Section.objects.filter(
            ledger__user=request.user,
            is_pinned=True
        ).order_by('ledger__sort_order', 'order')
    }