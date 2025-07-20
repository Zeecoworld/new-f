"""
URL configuration for fmecoursera project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.http import HttpResponse
from fme.urls import documented_urls
from django.urls import path, re_path, include
from fme.helpers.schema_generator import run_get_schema_view

schema_view = run_get_schema_view(documented_urls)


def fme_hello(request):
    return HttpResponse("Welcome to fme api.", content_type="text/plain")

urlpatterns = [
    path('', fme_hello),
    path('admin/', admin.site.urls),
    path('api/', include(documented_urls)),

    # doc
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
