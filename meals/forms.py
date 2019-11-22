from django import forms


class MealForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Dodaj', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))