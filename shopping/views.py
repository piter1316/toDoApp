from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from django.views.decorators.http import require_POST

from shopping.forms import ShoppingListForm
from shopping.models import ShoppingList, Products


@login_required(login_url='/accounts/login')
def shopping_list_index(request):
    shopping_lists = ShoppingList.objects.filter(user_id=request.user.id)
    shopping_lists_dict = {}
    form = ShoppingListForm(request.POST)
    for i in range(len(shopping_lists)):
        products_on_shopping_list = Products.objects.filter(shopping_list_id=shopping_lists[i].id)
        products = []
        for product in products_on_shopping_list:
            product_quantity = {product.product_name: product.quantity}
            products.append(product_quantity)

        shopping_lists_dict[shopping_lists[i]] = products
    print(shopping_lists_dict)
    context = {
        'shopping_lists': shopping_lists_dict,
        'form': form,
    }

    return render(request, 'shopping/index.html', context)


@require_POST
def add_shopping_list(request):
    form = ShoppingListForm(request.POST)

    if form.is_valid():
        new_shopping_list = ShoppingList(name=request.POST['name'], user_id=request.user)
        new_shopping_list.save()

    return redirect('shopping:shopping_list_index')


def delete_shopping_list(request, shopping_list_id):
    ShoppingList.objects.filter(id=shopping_list_id).delete()

    return redirect('shopping:shopping_list_index')
