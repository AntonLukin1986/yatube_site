from django.shortcuts import render
from django.http import HttpResponse

# Главная страница
def index(request):    
    return HttpResponse('Добро пожаловать!')


# Страница с постами, отфильтрованными по группам
def group_posts(request, any):
    return HttpResponse('Категории публикаций')
