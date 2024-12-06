from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import RegisterView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', LogoutView.as_view(template_name="sender:receiver_list"), name='logout'),
]