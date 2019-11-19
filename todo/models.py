from django.contrib.auth.models import User
from django.db import models

class Todo(models.Model):
    text = models.CharField(max_length=60)
    complete = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
