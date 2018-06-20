from django.shortcuts import render

def index(requsest):
    context = {}
    return render(requsest, 'todo/index.html', context)