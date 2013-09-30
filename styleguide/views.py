from django.shortcuts import render
from styleguide.utils import StyleguideLoader

def index(request):
    styleguide_loader = StyleguideLoader()
    styleguide_components = styleguide_loader.get_styleguide_components()

    context = { 'styleguide': styleguide_components }
    return render(request, "styleguide/index.html", context)