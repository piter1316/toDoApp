from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#316C9A')  # Domyślnie niebieski (50zł)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Ledger(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:  # Tylko przy tworzeniu nowego obiektu
            min_order = Ledger.objects.filter(user=self.user).aggregate(models.Min('sort_order'))[
                'sort_order__min']
            if min_order is not None:
                self.sort_order = min_order - 1
            else:
                self.sort_order = 0
        super().save(*args, **kwargs)


class Section(models.Model):
    name = models.CharField(max_length=100)
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='sections')
    order = models.IntegerField(default=0)
    is_pinned = models.BooleanField(default=False)

    # NOWE POLA BUDŻETOWE
    income = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Dochód")
    budget_account = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Budżet Konto")
    budget_cash = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Budżet Gotówka")

    def __str__(self):
        return f"{self.ledger.name} - {self.name}"

    @property
    def total_budget(self):
        return self.budget_account + self.budget_cash


class Expense(models.Model):
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='expenses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # NOWA FLAGA
    is_cash = models.BooleanField(default=False, verbose_name="Płatność gotówką")

    def __str__(self):
        return f"{self.title} - {self.amount} zł"


class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    hide_income = models.BooleanField(default=False)
    weather_stations = models.CharField(max_length=255, blank=True, null=True)
    home_station_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Ustawienia {self.user.username}"
