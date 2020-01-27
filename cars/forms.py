from django import forms

from . import models
from datetime import date


def get_date():
    year = str(date.today().year)
    month = str(date.today().month)
    if int(month) < 10:
        month = '0' + str(month)
    day = str(date.today().day)
    if int(day) < 10:
        day = '0' + str(day)
    return '{}-{}-{}'.format(year, month, day)


class CarForm(forms.ModelForm):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'Nazwa wyświetlana na stronie głównej'}))
    make = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'np. Audi'}))
    model = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'np. A3'}))
    year = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'np. 1997'}))
    engine = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'np. 1.6 MPI'}))
    power = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'np 101'}))
    mileage = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'np. 184000'}))
    logo = forms.FileField(required=False,
                           widget=forms.ClearableFileInput(attrs={'multiple': True,
                                                                  'class': 'form-control-file mb-2'}))
    image = forms.FileField(required=False,
                            widget=forms.ClearableFileInput(attrs={'multiple': True,
                                                                   'class': 'form-control-file mb-2'}))

    class Meta:
        model = models.Car
        fields = ['name', 'make', 'model', 'year', 'engine', 'power', 'mileage', 'logo', 'image']


class FuelFillForm(forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control p-0', 'type': 'date', 'value': get_date()}
    ))

    liters = forms.FloatField(widget=forms.NumberInput(
        attrs={'class': 'form-control  p-0', 'min': 1}
    ))

    kilometers = forms.FloatField(widget=forms.NumberInput(
        attrs={'class': 'form-control  p-0', 'min': 1}
    ))

    fuel_price = forms.FloatField(widget=forms.NumberInput(
        attrs={'class': 'form-control  p-0', 'min': 1}
    ))

    mileage = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control  p-0 ', 'min': 1}))



    class Meta:
        model = models.Fuel
        fields = ['date', 'liters', 'kilometers', 'fuel_price']

