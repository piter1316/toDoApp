import json
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView
from pymysql import IntegrityError

from cars import forms
from cars.forms import CarForm, FuelFillForm, AddServiceForm, PartServiceForm, BasePartServiceFormSet, InvoiceForm, \
    BaseInvoiceFormSet
from cars.models import Car, Fuel, Service, SparePart, Invoice
from myproject.settings import BASE_DIR
from django.core import serializers





def cars_home(request):
    user_cars = Car.objects.filter(user=request.user, sold=False)
    user_sold_cars = Car.objects.filter(user=request.user, sold=True)
    new_car_form = CarForm(request.POST)
    context = {
        'user_cars': user_cars,
        'form': new_car_form,
        'user_sold_cars': user_sold_cars
    }
    return render(request, 'cars/home.html', context)


def car_details(request, car_id):
    car = Car.objects.filter(pk=car_id, user=request.user)
    form = CarForm(request.POST, request.FILES)
    car_fuel_fill_list = Fuel.objects.filter(car_id=car_id).order_by('-date')
    car_fill_form = FuelFillForm()
    json_serializer = serializers.get_serializer("json")()
    chart_dates = json_serializer.serialize(Fuel.objects.filter(car_id=car_id).order_by('date'), ensure_ascii=False)
    service_list = Service.objects.select_related().filter(car_id=car_id).order_by('date')
    service_dictionary = {}
    for service in service_list:
        parts_sum = 0
        spare_parts_in_service = SparePart.objects.filter(service_id=service).order_by('service', 'price')
        invoices_in_service = Invoice.objects.filter(service_id=service)
        for part in spare_parts_in_service:
            parts_sum += part.price
        # print(service,'\n',
        #       SparePart.objects.filter(service_id=service), '\n',
        #       Invoice.objects.filter(service_id=service), '\n'
        #       )
        service_dictionary[service] = [spare_parts_in_service, invoices_in_service, parts_sum]

    context = {
        'car': car,
        'form': form,
        'car_fuel_fill_list': car_fuel_fill_list,
        'car_fill_form': car_fill_form,
        'chart_dates': chart_dates,
        'service_dictionary': service_dictionary
    }
    return render(request, 'cars/car_details.html', context)


class CarUpdate(UpdateView):
    model = Car
    form_class = CarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.object.pk
        context['car'] = Car.objects.filter(pk=pk)
        return context

    def get_success_url(self):
        pk = self.object.pk
        location = os.path.join(BASE_DIR, 'media', 'user_uploads',
                                '{}-{}'.format(self.object.user.id, self.object.user),
                                '{}-{}'.format(self.object.pk, self.object.name), 'images')
        location_to_database = os.path.join('user_uploads',
                                            '{}-{}'.format(self.object.user.id, self.object.user),
                                            '{}-{}'.format(self.object.pk, self.object.name), 'images')
        fs = FileSystemStorage(location=location)
        image = self.object.image
        logo = self.object.logo
        if image:
            fs.save(str(self.object.image), image)
            self.object.image = os.path.join(location_to_database, str(self.object.image))
            self.object.save()
        if logo:
            fs.save(str(self.object.logo), logo)
            self.object.logo = os.path.join(location_to_database, str(self.object.logo))
            self.object.save()

        return '{}'.format(reverse('cars:car_details', kwargs={'car_id': pk}))


    template_name = 'cars/car_edit.html'
    # success_url = redirect('cars:car_details', Car.pk)


def add_new_car(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            car.user = request.user
            car.save()
            location = os.path.join(BASE_DIR, 'media', 'user_uploads',
                                    '{}-{}'.format(request.user.id, request.user.username),
                                    '{}-{}'.format(car.pk, car.name), 'images')
            location_to_database = os.path.join('user_uploads',
                                    '{}-{}'.format(request.user.id, request.user.username),
                                    '{}-{}'.format(car.pk, car.name), 'images', )
            fs = FileSystemStorage(location=location)
            image = request.FILES.get('image', False)
            logo = request.FILES.get('logo', False)
            if image:
                fs.save(str(car.image), image)
                car.image = os.path.join(location_to_database, str(car.image))
                car.save()
            if logo:
                fs.save(str(car.logo), logo)
                car.logo = os.path.join(location_to_database, str(car.logo))
                car.save()


            return redirect('cars:cars_home')
    else:
        form = forms.CarForm()
    return redirect('cars:cars_home')


def add_fuel_fill(request, pk):
    if request.method == 'POST':
        form = FuelFillForm(request.POST, request.FILES)
        car = get_object_or_404(Car, pk=pk)
        filling = form.save(commit=False)
        filling.car_id = car
        filling.save()

        return HttpResponse('')


def delete_fuel_fill(request, pk):
    Fuel.objects.filter(pk=pk).delete()
    return HttpResponse('')


def add_service_form(request, pk):
    car = Car.objects.filter(pk=pk)
    car_obj = get_object_or_404(Car, pk=pk)
    form = AddServiceForm(request.POST)
    context = {
        'car': car,
        'form': form,
        'active_tab': 'service',
    }
    if request.method == 'POST':
        if form.is_valid():

            new_service = form.save(commit=False)
            new_service.car_id = car_obj
            new_service.save()
            return redirect('/cars/carDetails/{}#service'.format(pk))
        else:
            return render(request, 'cars/addService.html', context)
    else:
        return render(request, 'cars/addService.html', context)


def edit_parts_services(request, car_id, service_id):
    service_instance = get_object_or_404(Service, pk=service_id)
    car_id = car_id
    part_service_form_set = formset_factory(PartServiceForm, formset=BasePartServiceFormSet, extra=0, min_num=1)
    car_services = SparePart.objects.filter(service_id=service_id)

    service_data = [{'part_service': l.name, 'price': l.price, 'service': l.service}
                    for l in car_services]

    if request.method == 'POST':
        part_service_formset = part_service_form_set(request.POST)
        new_links = []
        for link_form in part_service_formset:
            if link_form.is_valid():
                anchor = link_form.cleaned_data.get('part_service')
                url = link_form.cleaned_data.get('price')
                service = link_form.cleaned_data.get('service')
                if anchor and url:
                    new_links.append(SparePart(service_id=service_instance, name=anchor, price=url, service=service))
        try:
            with transaction.atomic():
                SparePart.objects.filter(service_id=service_instance).delete()
                SparePart.objects.bulk_create(new_links)
                messages.success(request, 'Zmiany zapisane')
        except IntegrityError:
            messages.error(request, 'There was an error saving your profile.')
            return redirect(reverse('profile-settings'))
    else:
        part_service_formset = part_service_form_set(initial=service_data)
    context = {

        'part_service_formset': part_service_formset,
        'service_instance': service_instance,
        'car_id': car_id
    }
    return render(request, 'cars/editPartsServices.html', context)


def edit_invoices(request, car_id, service_id):
    service_instance = get_object_or_404(Service, pk=service_id)
    car_id = car_id
    invoice_form_set = formset_factory(InvoiceForm, formset=BaseInvoiceFormSet, extra=0, min_num=1)
    user_invoices = Invoice.objects.filter(service_id=service_id)
    invoice_data = [{'name': l.name, 'file': l.file}
                 for l in user_invoices]
    if request.method == 'POST':
        invoice_formset = invoice_form_set(request.POST, request.FILES)
        new_invoices = []
        for link_form in invoice_formset:
            if link_form.is_valid():
                name = link_form.cleaned_data.get('name')
                file = link_form.cleaned_data.get('file')
                if name:
                    new_invoices.append(Invoice(service_id=service_instance, name=name, file=file))
        try:
            with transaction.atomic():
                Invoice.objects.filter(service_id=service_instance).delete()
                Invoice.objects.bulk_create(new_invoices)
                print(new_invoices)
                messages.success(request, 'Zmiany zapisane')
        except IntegrityError:
            messages.error(request, 'There was an error saving your profile.')
            return redirect(reverse('profile-settings'))
    else:
        invoice_formset = invoice_form_set(initial=invoice_data)
    context = {

        'invoice_formset': invoice_formset,
        'service_instance': service_instance,
        'car_id': car_id
    }
    return render(request, 'cars/editInvoices.html', context)


def delete_service(request, car_id, service_id):
    Service.objects.filter(id=service_id).delete()
    return redirect('/cars/carDetails/{}#service'.format(car_id))