from django import forms
from django.forms.formsets import BaseFormSet

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

    fuel_price = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': 'form-control  p-0', 'min': 1, 'max': 99.99}
    ))

    mileage = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control  p-0 ', 'min': 1}))

    class Meta:
        model = models.Fuel
        fields = ['date', 'liters', 'kilometers', 'fuel_price', 'mileage']


class AddServiceForm(forms.ModelForm):

    date = forms.DateField(widget=forms.DateInput(
        attrs={'class': 'form-control p-0', 'type': 'date', 'value': get_date()}
    ))
    mileage = forms.IntegerField(required=False, widget=forms.NumberInput(
        attrs={'class': 'form-control  p-0 ', 'min': 1, 'placeholder': 'Podaj przebieg w dniu serwisu'}))

    class Meta:
        model = models.Service
        fields = ['date', 'mileage']


class LinkForm(forms.Form):
    """
    Form for individual user links
    """
    anchor = forms.CharField(
                    max_length=100,
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Link Name / Anchor Text',
                    }),
                    required=False)
    url = forms.CharField(
                    widget=forms.TextInput(attrs={
                        'placeholder': 'URL',
                    }),
                    required=False)
    service = forms.BooleanField(required=False)

class BaseLinkFormSet(BaseFormSet):
    def clean(self):
        """
        Adds validation to check that no two links have the same anchor or URL
        and that all links have both an anchor and URL.
        """
        if any(self.errors):
            return

        anchors = []
        urls = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                anchor = form.cleaned_data['anchor']
                url = form.cleaned_data['url']

                # Check that no two links have the same anchor or URL
                if anchor and url:
                    if anchor in anchors:
                        duplicates = True
                    anchors.append(anchor)

                    if url in urls:
                        duplicates = True
                    urls.append(url)

                if duplicates:
                    raise forms.ValidationError(
                        'Links must have unique anchors and URLs.',
                        code='duplicate_links'
                    )

                # Check that all links have both an anchor and URL
                if url and not anchor:
                    raise forms.ValidationError(
                        'All links must have an anchor.',
                        code='missing_anchor'
                    )
                elif anchor and not url:
                    raise forms.ValidationError(
                        'All links must have a URL.',
                        code='missing_URL'
                    )