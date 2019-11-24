from django import forms

from meals.models import Ingredient


class MealForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'Danie', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))


class IngredientForm(forms.Form):

    shop = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Sklep', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))

    quantity = forms.IntegerField(widget=forms.NumberInput(
        attrs={'value': 1,
               'class': 'form-control'}))


class MealOptionForm(forms.Form):
    meal_option = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Nowy posiłek', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))

