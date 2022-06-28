"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.contrib.auth.decorators import login_required

from myproject import settings
from todo import views


@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('', include('todo.urls'), name='todo'),
    path('', include('passwordGenerator.urls')),
    path('', include('accounts.urls')),
    path('', include('shopping.urls')),
    path('', include('meals.urls')),
    path('', include('cars.urls')),
    path('', include('exchange_rates.urls')),
    path('', include('receipts.urls')),
    url(r'^media/(?P<path>.*)$', protected_serve, {'document_root': settings.MEDIA_ROOT}),

]
