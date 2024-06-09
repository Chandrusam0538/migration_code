# # from django.urls import path


# from django.contrib import admin
# from django.urls import path
# from migrationapp import views

# urlpatterns = [ 
#     path('', views.login, name='home'),  # Set login view as the home page
#     path('Signup/', views.signup, name='SignUp'),
#     path('login/', views.login, name='login'),
#     path('board/', views.board, name='board'),
#     # path('dashboard/', views.dashboard, name='dashboard'),
#     path('Database_Connectivity/', views.dashboard, name='dashboard'),

#     path('display_data/', views.data_catalogue, name='data_catalogue'),
#     # path('scan_and_store_data/', views.scan_and_store_data, name='scan_and_store_data'),
#     path('data_mig/', views. data_mig, name='data_mig'),
#     # Add other necessary paths
# ]



from django.contrib import admin
from django.urls import path
from migrationapp import views

urlpatterns = [ 
    path('', views.login, name='home'),  # Set login view as the home page
    path('signup/', views.new_user, name='new_user'),
    path('login/', views.login, name='login'),
    path('board/', views.board, name='board'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    path('Database_Connectivity/', views.dashboard, name='dashboard'),

    path('display_data/', views.data_catalogue, name='data_catalogue'),
    # path('scan_and_store_data/', views.scan_and_store_data, name='scan_and_store_data'),
    path('data_mig/', views. data_mig, name='data_mig'),
    # Add other necessary paths
]



#signup fuct
# def new_user(request):
#     if request.method == "POST":
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         re_enter_password = request.POST.get('Re_enter_password')

#         # Check if passwords match
#         if password != re_enter_password:
#             return HttpResponse("Passwords do not match. Please try again.")

#         try:
#             # Create the user
#             user = User.objects.create_users(username=username, email=email, password=password)
#             # Optionally, you can set additional fields
#             user.save()
#             return redirect('login')  # Redirect to login page after successful signup
#         except Exception as e:
#             logger.error(f"Failed to create user: {e}")
#             return HttpResponse(f"Failed to create user. Please try again. Error: {e}")

#     return render(request, 'migrationapp/signup.html')
