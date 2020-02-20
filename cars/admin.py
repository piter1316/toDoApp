from django.contrib import admin

# Register your models here.
from cars.models import Car, Invoice, Fuel, Service, SparePart

admin.site.register(Car)
admin.site.register(Fuel)
admin.site.register(Service)
admin.site.register(SparePart)
admin.site.register(Invoice)