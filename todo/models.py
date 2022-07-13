from django.contrib.auth.models import User
from django.db import models


class ToDoMain(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.TextField(blank=True, null=True)
    complete = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'todo_main'


class Todo(models.Model):
    text = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    to_do_main = models.ForeignKey(ToDoMain, on_delete=models.CASCADE)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'todo_todo'


class TodoTodostep(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    complete = models.BooleanField(default=False)
    user = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'todo_todostep'
