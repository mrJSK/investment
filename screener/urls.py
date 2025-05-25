from django.urls import include, path
from .views import scanner_view

urlpatterns = [
    path('', scanner_view, name='scanner'), 
    path('run/', scanner_view, name='scanner'),

]
