from django.contrib import admin
from .models import WeaponType, Caliber, Weapon, Magazine, Shooting, Cleaning, Accessory, AmmoSafe

admin.site.register(WeaponType)
admin.site.register(Caliber)
admin.site.register(Weapon)
admin.site.register(Magazine)
admin.site.register(Shooting)
admin.site.register(Cleaning)
admin.site.register(Accessory)
admin.site.register(AmmoSafe)
