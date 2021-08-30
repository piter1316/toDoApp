import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.views.decorators.http import require_POST

from meals.models import Unit, Meal, Ingredient, MealsList, MealIngredient, Shop
from myproject.settings import BASE_DIR
from shopping.forms import ShoppingListForm, ProductsForm
from shopping.models import ShoppingList, Products, Checklist


@login_required(login_url='/accounts/login')
def shopping_list_index(request):
    shopping_lists = ShoppingList.objects.filter(user_id=request.user.id)
    shopping_lists_dict = {}
    form = ShoppingListForm(request.POST)
    form_2 = ProductsForm(request.POST)
    units = Unit.objects.all()
    checklist = Checklist.objects.filter(user=request.user.id)

    for i in range(len(shopping_lists)):
        products_on_shopping_list = Products.objects.filter(shopping_list_id=shopping_lists[i].id)
        products = []
        for product in products_on_shopping_list:
            meals_with_product = []
            generated_meals_with_product = []
            if not product.bought:
                try:
                    ingredient = Ingredient.objects.get(name__contains=product, user_id=request.user)
                    meals_with_product_query = MealIngredient.objects.filter(ingredient_id=ingredient)
                    for item in meals_with_product_query:
                        meals_with_product.append(item)
                except Exception:
                    pass
            for meal in meals_with_product:
                query_set = MealsList.objects.filter(meal_id=meal.meal_id_id)
                if len(query_set) > 0:
                    generated_meals_with_product.append(query_set[0])

            product_quantity_bought = [product.quantity, product.bought, product.id, product.unit, generated_meals_with_product]
            product_quantity = {product: product_quantity_bought}
            products.append(product_quantity)
        shopping_lists_dict[shopping_lists[i]] = products
    context = {
        'shopping_lists': shopping_lists_dict,
        'form': form,
        'form_2': form_2,
        'units': units,
        'checklist': checklist
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
    file = open(os.path.join(BASE_DIR, 'shopping/templates/shopping/add_to_shopping_list.html'), encoding='utf-8')
    file_lines = file.readlines()
    html = ' '.join(file_lines)
    html = html.replace('####', str(new_product.pk))
    html = html.replace('###product##', str(new_product))
    try:
        ingredient = Ingredient.objects.get(name__contains=new_product, user_id=request.user)
        meals_with_product_query = MealIngredient.objects.filter(ingredient_id=ingredient)
        html = html.replace("""<small class="mb-1">Brak posiłków zawierających {}</small>""".format(str(new_product)), '')
        loop_html_total = ""
        for meal in meals_with_product_query:
            query_set = MealsList.objects.filter(meal_id=meal.meal_id_id)
            if len(query_set) > 0:
                loop_html = """
                <li class="list-group-item p-0">
                  <small>
                    <a class="text-dark" href="/mealsEdit">{}</a>: <a class="text-dark" href="/mealsEdit/edit_meal_ingredients/{}">{}</a>
                  </small>
                </li>
                """.format(str(query_set[0].meal_option), str(query_set[0].meal_id), query_set[0])
                loop_html_total += loop_html

        html = html.replace('###LOOP###', loop_html_total)
    except Exception as e:
        html = html.replace('###LOOP###', '')

    return HttpResponse(html)


def update_product(request, product_id):
    old_name = ''
    old_name_guery = Products.objects.filter(pk=product_id)
    for query in old_name_guery:
        old_name = str(query.product_name)
    new_name = request.POST['new_product_name'].lower()
    new_quantity = request.POST['new_quantity']
    new_unit = request.POST['new_unit']
    Products.objects.filter(pk=product_id).update(product_name=new_name, quantity=new_quantity, unit=new_unit)
    if old_name != new_name:
        return redirect('shopping:shopping_list_index')
    else:
        return HttpResponse(str(new_quantity) + '_' + str(new_unit))


def bought(request, id):
    product = Products.objects.get(pk=id)
    product.bought = True
    product.save()
    return HttpResponse('Product: {} marked as bought'.format(product))


def delete_bought(request, shopping_list_id):
    Products.objects.filter(bought__exact=True, shopping_list_id=shopping_list_id).delete()
    return HttpResponse('Selected products deleted from list')


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


def add_from_checklist(request):
    for element in request.POST.getlist('checkitem[]'):
        product_name = element.split('###')[0]
        shop_name = element.split('###')[1]
        shopping_list_to_update = ShoppingList.objects.filter(name=shop_name, user_id_id=request.user)[0]
        new_shopping_product = Products(product_name=product_name, quantity=1, bought=0, shopping_list_id=shopping_list_to_update, unit_id=1)
        new_shopping_product.save()

    return redirect('shopping:shopping_list_index')


def edit_check_list(request):
    checklist = Checklist.objects.filter(user=request.user.id)
    user_shops = Shop.objects.filter(user_id= request.user)
    context = {
        'checklist': checklist,
        'user_shops': user_shops,
    }
    return render(request, 'shopping/edit_checklist.html', context)


def add_item(request):
    if request.method == 'POST':
        print(request.POST)
        shop = get_object_or_404(Shop, pk=request.POST['addNewPosToCheckListShop'])
        new_checklist_position = Checklist(user_id=request.user.id, product_name=request.POST['addNewPosToCheckListName'],
                                           shop_id=shop.pk)
        new_checklist_position.save()
    return redirect('shopping:edit_check_list')


def delete_item(request, item_id):
    print(item_id)
    Checklist.objects.filter(user_id=request.user, pk=item_id).delete()
    return redirect('shopping:edit_check_list')


def update_item(request, item_id):
    if request.method == 'POST':
        new_name = request.POST['updatePosOnCheckListName']
        new_shop = get_object_or_404(Shop, pk=request.POST['updatePosOnCheckListShop'])
        Checklist.objects.filter(pk=item_id).update(product_name=new_name, shop_id=new_shop)
    return redirect('shopping:edit_check_list')