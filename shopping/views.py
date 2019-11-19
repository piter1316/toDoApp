from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from shopping.models import ShoppingList, Products


@login_required(login_url='/accounts/login')
def shopping_list_index(request):
    shopping_lists = ShoppingList.objects.filter(user_id=request.user.id)
    shopping_lists_dict = {}
    for i in range(len(shopping_lists)):
        products_on_shopping_list = Products.objects.filter(shopping_list_id=shopping_lists[i].id)
        products = []
        for product in products_on_shopping_list:
            products.append(product.product_name)

        shopping_lists_dict[shopping_lists[i].name] = products
    print(shopping_lists_dict)
    products = Products.objects.all()

    return render(request, 'shopping/index.html', {'shopping_lists': shopping_lists_dict})