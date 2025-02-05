from django.urls import path
from .views import home, incomplete_financial_data, edit_financial_data ,financial_data_list

from . import views

urlpatterns = [
    path("", views.home, name="home"),
     path("incomplete-financial-data/", incomplete_financial_data, name="incomplete_financial_data"),
    path("edit-financial-data/<int:pk>/", edit_financial_data, name="edit_financial_data"),
    path("financial-data/", financial_data_list, name="financial_data_list"),
]
