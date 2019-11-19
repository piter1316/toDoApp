from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from shopping.models import ShoppingList, Products


def shopping_list_index(request):

    shopping_lists = ShoppingList.objects.filter(user_id=request.user)
    products = Products.objects.all()
    query = request.GET.get("q")
    if query:
        shopping_lists = shopping_lists.filter(
            Q(name__icontains=query)
        ).distinct()
        products = products.filter(
            Q(name__icontains=query)
        ).distinct()
        return render(request, 'shopping/index.html', {
            'shopping_lists': shopping_lists,
            'products': products,
        })
    else:
        return render(request, 'shopping/index.html', {'shopping_lists': shopping_lists})