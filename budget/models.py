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

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=100)
    ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, related_name='sections')
    order = models.IntegerField(default=0)

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


from django.db import models

# Create your models here.
