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

    unit = forms.ChoiceField(label='Units', widget=forms.Select(
                             attrs={'class': 'form-control'}
                             ))

    EXTRA_CHOICES = [
        ('AP', 'All Promotions'),
        ('LP', 'Live Promotions'),
        ('CP', 'Completed Promotions'),
    ]

    # def __init__(self, *args, **kwargs):
    #     super(PromotionListFilterForm, self).__init__(*args, **kwargs)
    #     choices = [(pt.id, unicode(pt)) for pt in PromotionType.objects.all()]
    #     choices.extend(EXTRA_CHOICES)
    #     self.fields['promotion_type'].choices = choices


class MealOptionForm(forms.Form):
    meal_option = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Nowy posiłek. Np: Podwieczorek', 'aria-label': 'shoppingList',
               'aria-describedby': 'add-btn'}))
