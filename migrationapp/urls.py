# from django.urls import path


from django.contrib import admin
from django.urls import path
from migrationapp import views

urlpatterns = [ 
    path('', views.login, name='home'),  # Set login view as the home page
    path('Signup/', views.signup, name='SignUp'),
    path('login/', views.login, name='login'),
    path('board/', views.board, name='board'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('Database_Connectivity/', views.dashboard, name='dashboard'),

    path('display_data/', views.data_catalogue, name='data_catalogue'),
    path('scan_and_store_data/', views.scan_and_store_data, name='scan_and_store_data'),
    path('data_mig/', views. data_mig, name='data_mig'),
    # Add other necessary paths
]
