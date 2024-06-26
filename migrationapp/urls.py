from django.contrib import admin
from django.urls import path
from migrationapp import views
from django.urls import path
from django.views.generic import RedirectView
from migrationapp import views

urlpatterns = [ 
    path('', views.login, name='home'),  
    path('Signup/', views.signup, name='Signup'),
    path('login/', views.login, name='login'),
    path('board/', views.board, name='board'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('Database_Connectivity/', views.dashboard, name='dashboard'),

    path('display_data/', views.data_catalogue, name='data_catalogue'),
    # path('scan_and_store_data/', views.scan_and_store_data, name='scan_and_store_data'),
    path('data_mig/', views. data_mig, name='data_mig'),
    path('db/', views. present_db, name='present_db'),
    # path('signup/', views.new_user, name='new_user'),
    path('server_user_view/', views.server_users_view, name='server_users_view'),

    path('databases/', views.database_display, name='database_display'),
    path('databases/<str:object_database>/', views.retrieve_metadata, name='retrieve_metadata'),

]    

