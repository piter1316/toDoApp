import json
import os
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.forms import formset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage

# Create your views here.
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView
from pymysql import IntegrityError

from cars import forms
from cars.forms import CarForm, FuelFillForm, AddServiceForm, LinkForm, BaseLinkFormSet, InvoiceForm
from cars.models import Car, Fuel, Service, SparePart, Invoice
from myproject.settings import BASE_DIR, MEDIA_ROOT
from django.core import serializers
import xlwt
from io import BytesIO, StringIO
import zipfile


def get_services_as_dict(services_list):
    service_total_cost = 0
    service_dictionary = {}
    for service in services_list:
        parts_sum = 0
        spare_parts_in_service = SparePart.objects.filter(service_id=service).order_by('service', 'price')
        invoices_in_service = Invoice.objects.filter(service_id=service)
        for part in spare_parts_in_service:
            parts_sum += part.price
        service_dictionary[service] = [spare_parts_in_service, invoices_in_service, parts_sum]
        service_total_cost += parts_sum
    return service_dictionary, service_total_cost


@login_required(login_url='/accounts/login')
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


def get_stats_data(j_dict):
    years = sorted(list(set([entry.get('fields').get('date').split('-')[0] for entry in j_dict])), reverse=True)
    current_year = str(datetime.today().year)
    current_month = datetime.today().month
    stats_calendar = {}
    months_txt = {
        '01': 'Styczeń', '02': 'Luty', '03': 'Marzec', '04': 'Kwiecień',
        '05': 'Maj', '06': 'Czerwiec', '07': 'Lipiec', '08': 'Sierpień',
        '09': 'Wrzesień', '10': 'Październik', '11': 'Listopad', '12': 'Grudzień',
    }
    for year in years:
        max_month = current_month if year == current_year else 12
        stats_calendar[year] = {f"{month:02d}": {'data': [], 'summary': []} for month in range(1, max_month + 1)}
    for year in years:
        for entry in j_dict:
            if entry.get('fields').get('date').startswith(year):
                month = entry.get('fields').get('date').split('-')[1]
                stats_calendar[year][month]['data'].append(entry)
    for month_data in stats_calendar.values():
        for month, content in month_data.items():
            total_liters = 0.0
            total_cost = 0.0

            for record in content['data']:
                liters = record['fields']['liters']
                price = float(record['fields']['fuel_price'])
                total_liters += liters
                total_cost += liters * price
            content['summary'] = [
                round(total_liters, 2),
                round(total_cost, 2),
                months_txt[month]
            ]
    for year_data in stats_calendar.values():
        for month_data in year_data.values():
            for entry in month_data['data']:
                liters = entry['fields']['liters']
                price = float(entry['fields']['fuel_price'])
                entry['fields']['cost'] = round(liters * price, 2)
    return stats_calendar


@login_required(login_url='/accounts/login')
def car_details(request, car_id):
    total_fuel = 0
    total_km = 0
    lowest_average = 0
    highest_average = 0
    total_fuel_cost = 0
    month_average = 0
    km_month_average = 0
    car = Car.objects.filter(pk=car_id, user=request.user)
    form = CarForm(request.POST, request.FILES)
    car_fuel_fill_list = Fuel.objects.filter(car_id=car_id).order_by('-date')
    car_fill_form = FuelFillForm()
    json_serializer = serializers.get_serializer("json")()
    chart_dates = json_serializer.serialize(Fuel.objects.filter(car_id=car_id).order_by('date'), ensure_ascii=False)
    service_list = Service.objects.select_related().filter(car_id=car_id).order_by('-date')
    total_fuel_list = []
    total_km_list = []
    averages_list = []
    fuel_cost_list = []
    dates_list = []
    for fuel in car_fuel_fill_list:
        total_fuel_list.append(fuel.liters)
        total_km_list.append(fuel.kilometers)
        averages_list.append(round(fuel.liters/fuel.kilometers * 100, 2))
        fuel_cost_list.append(fuel.liters * float(fuel.fuel_price))
        dates_list.append(fuel.date)
    if car_fuel_fill_list:
        first_last_fuel_time_interval = max(dates_list) - min(dates_list)
        first_last_fuel_time_interval_months = first_last_fuel_time_interval.days / 31
        total_fuel = round(sum(total_fuel_list), 2)
        total_km = round(sum(total_km_list), 2)
        total_fuel_cost = round(sum(fuel_cost_list), 2)
        lowest_average = min(averages_list)
        highest_average = max(averages_list)
        if first_last_fuel_time_interval_months:
            month_average = round(total_fuel_cost / first_last_fuel_time_interval_months, 2)
            km_month_average = round(total_km / first_last_fuel_time_interval_months, 2)

    try:
        average_consumption = round(total_fuel / total_km * 100, 2)
    except ZeroDivisionError:
        average_consumption = 0

    try:
        last_service = service_list[0]
    except IndexError:
        last_service = ''

    stats_data = get_stats_data(json.loads(chart_dates))
    context = {
        'car': car,
        'form': form,
        'car_fuel_fill_list': car_fuel_fill_list,
        'car_fill_form': car_fill_form,
        'chart_dates': chart_dates,
        'service_dictionary': get_services_as_dict(service_list)[0],
        'last_service': last_service,
        'average_consumption': average_consumption,
        'service_total_cost': get_services_as_dict(service_list)[1],
        'lowest_average': lowest_average,
        'highest_average': highest_average,
        'total_fuel_cost': total_fuel_cost,
        'month_average': month_average,
        'total_fuel': total_fuel,
        'total_km': total_km,
        'km_month_average': km_month_average,
        'stats_data': stats_data,
    }
    return render(request, 'cars/car_details.html', context)


class CarUpdate(UpdateView):
    model = Car
    form_class = CarForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.object.pk
        context['car'] = Car.objects.filter(pk=pk)
        context['return_url'] = '{}#info'.format(reverse('cars:car_details', kwargs={'car_id': pk}))
        return context

    def get_success_url(self):
        pk = self.object.pk
        # location = os.path.join(BASE_DIR, 'media', 'user_uploads',
        #                         '{}-{}'.format(self.object.user.id, self.object.user),
        #                         '{}-{}'.format(self.object.pk, self.object.name), 'images')
        # location_to_database = os.path.join('media', 'user_uploads',
        #                                     '{}-{}'.format(self.object.user.id, self.object.user),
        #                                     '{}-{}'.format(self.object.pk, self.object.name), 'images')
        # fs = FileSystemStorage(location=location)
        # image = self.object.image
        # logo = self.object.logo
        # if image:
        #     fs.save(str(self.object.image), image)
        #     self.object.image = os.path.join(location_to_database, str(self.object.image))
        #     self.object.save()
        # if logo:
        #     fs.save(str(self.object.logo), logo)
        #     self.object.logo = os.path.join(location_to_database, str(self.object.logo))
        #     self.object.save()

        return '{}#info'.format(reverse('cars:car_details', kwargs={'car_id': pk}))

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
        context = {}

        return redirect('/cars/carDetails/{}#service'.format(pk))


def delete_fuel_fill(request, pk):
    fuel = Fuel.objects.filter(pk=pk)
    car_id = fuel[0].car_id_id
    Fuel.objects.filter(pk=pk).delete()
    return redirect('/cars/carDetails/{}#service'.format(car_id))


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

    LinkFormSet = formset_factory(LinkForm, formset=BaseLinkFormSet, extra=0, min_num=1)
    # Get our existing link data for this user.  This is used as initial data.
    user_links = SparePart.objects.filter(service_id=service_id)

    link_data = [{'part_service': l.name, 'price': l.price, 'service': l.service}
                 for l in user_links]

    if request.method == 'POST':
        link_formset = LinkFormSet(request.POST)
        new_links = []

        for link_form in link_formset:
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
        return redirect('/cars/carDetails/{}#service'.format(car_id))
    else:

        link_formset = LinkFormSet(initial=link_data)

    context = {

        'link_formset': link_formset,
        'service_instance': service_instance,
        'car_id': car_id
    }

    return render(request, 'cars/editPartsServices.html', context)


def edit_invoices(request, car_id, service_id):
    service_instance = get_object_or_404(Service, pk=service_id)
    car_instance = get_object_or_404(Car, pk=car_id)
    service_invoices = Invoice.objects.filter(service_id=service_id)

    location = os.path.join(BASE_DIR, 'media', 'user_uploads',
                            '{}-{}'.format(request.user.id, request.user.username),
                            '{}-{}'.format(car_instance.pk, car_instance.name), 'invoices')
    location_to_database = os.path.join('media', 'user_uploads',
                                        '{}-{}'.format(request.user.id, request.user.username),
                                        '{}-{}'.format(car_instance.pk, car_instance.name), 'invoices', )

    form = InvoiceForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            new_invoice = form.save(commit=False)
            fs = FileSystemStorage(location=location)
            file = request.FILES.get('file', False)
            fs.save(str(new_invoice.file), file)
            new_invoice.file = os.path.join(location_to_database, str(new_invoice.file))
            new_invoice.service_id = service_instance
            new_invoice.save()
    context = {
        'service_instance': service_instance,
        'car_id': car_id,
        'service_invoices': service_invoices,
        'location_to_database': location_to_database,
        'form': form,
    }
    return render(request, 'cars/editInvoices.html', context)


def delete_service(request, car_id, service_id):
    invoices = Invoice.objects.filter(service_id=service_id)
    for invoice in invoices:
        path = os.path.join(BASE_DIR, str(invoice.file))
        try:
            default_storage.delete(path)
        except Exception:
            pass
    Service.objects.filter(id=service_id).delete()

    return redirect('/cars/carDetails/{}#service'.format(car_id))


def edit_service_details(request, car_id, service_id):
    form = AddServiceForm(request.POST)
    context = {
        'form': form
    }
    return render(request, 'cars/editServiceDetails.html', context)


class ServiceDeailsUpdate(UpdateView):
    model = Service
    form_class = AddServiceForm
    template_name = 'cars/editServiceDetails.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        car_id = self.object.car_id.pk
        context['reverse_url'] = '{}#service'.format(reverse('cars:car_details', kwargs={'car_id': car_id}))
        return context

    def get_success_url(self):
        car_id = self.object.car_id.pk
        return '{}#service'.format(reverse('cars:car_details', kwargs={'car_id': car_id}))


def delete_invoice(request, car_id, service_id, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    path = os.path.join(BASE_DIR, str(invoice.file))
    try:
        default_storage.delete(path)
    except Exception:
        pass
    Invoice.objects.filter(pk=invoice_id).delete()

    return redirect('/cars/carDetails/{}/{}/editInvoices'.format(car_id, service_id))


def download_history(request, car_id):
    services_list = Service.objects.select_related().filter(car_id=car_id).order_by('-date')
    services_dict = get_services_as_dict(services_list)[0]
    car_name = Car.objects.filter(pk=car_id)[0].name

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Historia")
    row_num = 0
    column_font_style = xlwt.XFStyle()
    # headers are bold
    column_font_style.font.bold = True

    columns = ['Data', 'Przebieg', 'Część/Usługa', 'Cena [PLN]']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], column_font_style)
    ws.col(0).width = 3000
    ws.col(1).width = 3000
    ws.col(2).width = 7500
    ws.col(3).width = 3000

    font_style = xlwt.XFStyle()

    sum_font_style = xlwt.XFStyle()
    sum_font_style.font.bold = True
    for service, elements in services_dict.items():
        print(service)
        row_num = row_num + 1
        ws.write(row_num, 0, str(service.date), font_style)
        ws.write(row_num, 1, service.mileage, font_style)
        for element in elements[0]:
            ws.write(row_num, 2, str(element), font_style)
            ws.write(row_num, 3, element.price, font_style)
            row_num += 1
        ws.write(row_num, 2, 'SUMA', sum_font_style)
        ws.write(row_num, 3, elements[2], sum_font_style)
        row_num += 1
    ws.write(row_num + 2, 0, 'SUMA CAŁKOWITA:', column_font_style)
    ws.write(row_num + 2, 3, get_services_as_dict(services_list)[1], column_font_style)
    excel_save_path = os.path.join(BASE_DIR, 'media', 'user_uploads',
                                   '-'.join([str(request.user.id), request.user.username]),
                                   '-'.join([car_id, car_name]), 'service_history.xls')
    excel_mkdir_path = os.path.join(BASE_DIR, 'media', 'user_uploads',
                                    '-'.join([str(request.user.id), request.user.username]),
                                    '-'.join([car_id, car_name]))
    user_invoices_paths = [(os.path.join(BASE_DIR, invoice.file.path), str(invoice.service_id.date)) for invoice in
                           Invoice.objects.select_related().filter(service_id_id__in=[
                               service.id for service in services_list]).order_by('service_id_id__date')
                           ]
    byte_data = BytesIO()
    try:
        wb.save(excel_save_path)
    except FileNotFoundError:
        print('create dir')
        os.mkdir(excel_mkdir_path)
        wb.save(excel_save_path)
    zip_file = zipfile.ZipFile(byte_data, "w")
    for file in user_invoices_paths:
        url = file[0]
        if 'media/media' in url:
            url = url.replace('media/media', 'media')
        filename = os.path.basename(os.path.normpath(url))
        zip_file.write(url, os.path.join(file[1], filename))
    zip_file.write(excel_save_path, f'historia_serwisowa_{car_name}.xls')
    zip_file.close()
    response = HttpResponse(byte_data.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename=historia_serwisowa_{car_name}.zip'

    return response
