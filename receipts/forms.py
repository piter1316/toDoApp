from datetime import date

from django import forms
from django.forms.formsets import BaseFormSet

from . import models
from .models import Receipt


class ReceiptForm(forms.ModelForm):
    name = forms.CharField(max_length=100, widget=forms.TextInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'Nazwa paragonu'}))
    purchase_date = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control p-0', 'type': 'date'}, format='%Y-%m-%d'
    ))
    price = forms.DecimalField(required=True,
                               widget=forms.NumberInput(attrs={
                                   'placeholder': 'Cena', 'required': 'true', 'class': 'form-control'
                               }))
    shop = forms.CharField(max_length=100, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'Sklep'}))

    notes = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'Notatki'}))

    warranty = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control mb-2',
               'placeholder': 'ilość dni'}))

    file = forms.FileField(required=False,
                           widget=forms.FileInput(attrs={
                               'class': 'form-control-file',
                           }))

    class Meta:
        model = models.Receipt
        fields = ['name', 'purchase_date', 'price', 'shop', 'notes', 'warranty']