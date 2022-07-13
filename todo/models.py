from django.contrib.auth.models import User
from django.db import models


class ToDoMain(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'todo_main'


class Todo(models.Model):
    text = models.CharField(max_length=200)
    complete = models.BooleanField(default=False)
    to_do_main = models.ForeignKey(ToDoMain, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'todo_todo'


class TodoTodostep(models.Model):
    todo = models.ForeignKey(Todo, models.DO_NOTHING)
    text = models.TextField(blank=True, null=True)
    complete = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'todo_todostep'
