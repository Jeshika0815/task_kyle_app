# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('/', views.welcome, name='visitor'),
    path('/login', views.login, name='login'),
    path('/signin', views.signin, name='signin'),
    path('/dashboard', views.home, name='home'),
    path('/docs', views.docs, name='docs'),
    path('/register', views.confirm_schedule, name='register'),
    path('/edit', views.edit_schedule, name='edit'),
    path('/delete', views.delete_schedule, name='delete'),
]
