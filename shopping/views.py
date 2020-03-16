from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.views.decorators.http import require_POST

from meals.models import Unit, Meal, Ingredient, MealsList
from shopping.forms import ShoppingListForm, ProductsForm
from shopping.models import ShoppingList, Products


@login_required(login_url='/accounts/login')
def shopping_list_index(request):
    shopping_lists = ShoppingList.objects.filter(user_id=request.user.id)
    shopping_lists_dict = {}
    form = ShoppingListForm(request.POST)
    form_2 = ProductsForm(request.POST)
    units = Unit.objects.all()

    for i in range(len(shopping_lists)):
        products_on_shopping_list = Products.objects.filter(shopping_list_id=shopping_lists[i].id)
        products = []

        for product in products_on_shopping_list:
            meals_with_product = []
            generated_meals_with_product = []
            # if not product.bought:
            #     meals_with_product_query = Ingredient.objects.filter(name__contains=product.product_name, user=request.user)
            #
            #     for item in meals_with_product_query:
            #         meals_with_product.append(item)
            #
            # for meal in meals_with_product:
            #     query_set = MealsList.objects.filter(meal_id=meal.meal_id_id)
            #     if len(query_set) > 0:
            #         generated_meals_with_product.append(query_set[0])

            product_quantity_bought = [product.quantity, product.bought, product.id, product.unit, generated_meals_with_product]
            product_quantity = {product: product_quantity_bought}
            products.append(product_quantity)

        shopping_lists_dict[shopping_lists[i]] = products
    context = {
        'shopping_lists': shopping_lists_dict,
        'form': form,
        'form_2': form_2,
        'units': units
    }

    return render(request, 'shopping/index.html', context)


@require_POST
def add_shopping_list(request):
    form = ShoppingListForm(request.POST)
    if form.is_valid():
        new_shopping_list = ShoppingList(name=request.POST['name'].upper(), user_id=request.user)
        new_shopping_list.save()
    return redirect('shopping:shopping_list_index')


def delete_shopping_list(request, shopping_list_id):
    ShoppingList.objects.filter(id=shopping_list_id).delete()
    return redirect('shopping:shopping_list_index')


def delete_all_shopping_lists(request):
    ShoppingList.objects.filter(user_id=request.user).delete()
    return redirect('shopping:shopping_list_index')


@require_POST
def add_product(request, shopping_list_id):
    shopping_list = get_object_or_404(ShoppingList, pk=shopping_list_id)
    form = ProductsForm(request.POST)

    new_product = Products(shopping_list_id=shopping_list,
                           product_name=request.POST['product_name'].lower(),
                           quantity=request.POST['quantity'],
                           unit_id=request.POST['prod_unit'])
    new_product.save()
    return HttpResponse('')


def update_product(request, product_id):
    new_name = request.POST['new_product_name'].lower()
    new_quantity = request.POST['new_quantity']
    new_unit = request.POST['new_unit']
    Products.objects.filter(pk=product_id).update(product_name=new_name, quantity=new_quantity, unit=new_unit)
    return redirect('shopping:shopping_list_index')


def bought(request, id):
    product = Products.objects.get(pk=id)
    product.bought = True
    product.save()
    return redirect('shopping:shopping_list_index')


def delete_bought(request, shopping_list_id):
    Products.objects.filter(bought__exact=True, shopping_list_id=shopping_list_id).delete()
    return redirect('shopping:shopping_list_index')


def purge_list(request, shopping_list_id):
    Products.objects.filter(shopping_list_id=shopping_list_id).delete()
    return redirect('shopping:shopping_list_index')


def shopping_list_edit(request, shopping_list_id):
    list_to_edit = ShoppingList.objects.get(pk=shopping_list_id)
    list_to_edit.name = request.POST['name'].upper()
    list_to_edit.save()
    return redirect('shopping:shopping_list_index')


def bought_many(request):
    shopping_items_bought = request.POST.getlist('bought_checkbox')
    for item in shopping_items_bought:
        shopping_product = get_object_or_404(Products, pk=int(item))
        shopping_product.bought = True
        shopping_product.save()
    return redirect('shopping:shopping_list_index')
