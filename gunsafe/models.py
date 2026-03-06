from django.db import models
from django.contrib.auth.models import User


class WeaponType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class Caliber(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Weapon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weapons')
    name = models.CharField(max_length=100)
    weapon_type = models.ForeignKey(WeaponType, on_delete=models.SET_NULL, null=True, blank=True)
    caliber = models.ForeignKey(Caliber, on_delete=models.SET_NULL, null=True, blank=True)
    serial_no = models.CharField(max_length=100, blank=True, null=True)
    action = models.CharField(max_length=100, blank=True, null=True)
    total_rounds_fired = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.serial_no})"

    @property
    def last_shooting(self):
        return self.shootings.order_by('-date').first()

    @property
    def last_cleaning(self):
        return self.cleanings.order_by('-date').first()


class Magazine(models.Model):
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE, related_name='magazines')
    capacity = models.PositiveIntegerField()
    manufacturer = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.manufacturer or 'N/A'} - {self.capacity} rds ({self.weapon.name})"


class Shooting(models.Model):
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE, related_name='shootings')
    date = models.DateField()
    rounds = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.date} - {self.rounds} rds ({self.weapon.name})"


class Cleaning(models.Model):
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE, related_name='cleanings')
    date = models.DateField()

    def __str__(self):
        return f"Cleaned on {self.date} ({self.weapon.name})"


class Accessory(models.Model):
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE, related_name='accessories')
    accessory_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    date_bought = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.accessory_name} ({self.weapon.name})"


class AmmoSafe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ammo_inventory')
    caliber = models.ForeignKey(Caliber, on_delete=models.CASCADE)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    qty = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.caliber.name} - {self.qty} rds ({self.manufacturer or 'N/A'})"
