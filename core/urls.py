from django.urls import path
from django.contrib.auth import views as auth_views
from .views import index, register  # <-- THE FIX IS HERE

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'), # <-- This now works
    
    # Login & Logout URLs (from Part C)
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
]

