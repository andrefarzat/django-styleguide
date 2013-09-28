from django.shortcuts import render_to_response
from styleguide.utils import StyleguideLoader

def index(request):
    styleguide_loader = StyleguideLoader()
    styleguide_components = styleguide_loader.get_styleguide_components()

    return render_to_response("styleguide/index.html", { 'styleguide': styleguide_components })