from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home, incomplete_financial_data, edit_financial_data ,financial_data_list ,about ,contact ,delete_financial_data ,dashboard

from . import views

urlpatterns = [
    path("", views.home, name="home"),
     path("incomplete-financial-data/", incomplete_financial_data, name="incomplete_financial_data"),
    path("edit-financial-data/<int:pk>/", edit_financial_data, name="edit_financial_data"),
    path("financial-data/", financial_data_list, name="financial_data_list"),
    path('about/', about, name='about'),
     path('contact/', contact, name='contact'),
      path('login/', auth_views.LoginView.as_view(template_name='finance/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('delete-financial-data/<int:pk>/', delete_financial_data, name='delete_financial_data'),
    path('dashboard/', dashboard, name='dashboard'),

     

]
