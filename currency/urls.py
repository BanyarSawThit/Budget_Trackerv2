from django.urls import path

from currency import views

urlpatterns = [
    path('set/', views.set_currency, name='set_currency')
]