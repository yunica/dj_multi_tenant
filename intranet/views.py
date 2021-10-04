from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.


class MainPage(TemplateView):
    template_name = "adm/index.html"
