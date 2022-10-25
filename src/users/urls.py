from django.contrib.auth import views
from django.urls import path

from .views import Register, Settings


app_name = 'users'

urlpatterns = [
    path('login/', views.LoginView.as_view(template_name='users/auth.html'), name='login'),
    path('logout/', views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('register/', Register.as_view(), name="register"),
    path('settings/', Settings.as_view(), name="settings"),
]
