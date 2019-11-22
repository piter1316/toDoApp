from django import forms


class ShoppingListForm(forms.Form):
    name = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Nazwa listy zakupów', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))


class ProductsForm(forms.Form):
    product_name = forms.CharField(max_length=60, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Dodaj na listę', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))

