from django import forms


class MealForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'Danie', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn',
               'required': 'True'}))
    special = forms.BooleanField(required=False)


class IngredientForm(forms.Form):
    shop = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Sklep', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))

    quantity = forms.IntegerField(widget=forms.NumberInput(
        attrs={'value': 1,
               'class': 'form-control'}))
    unit = forms.ChoiceField(widget=forms.Select(
        attrs={'class': 'form-control'}
    ))


class MealOptionForm(forms.Form):
    meal_option = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Nowy posiłek. Np: Podwieczorek', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))
