# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='visitor'),
    path('login/', views.login, name='login'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout, name='logout'),
    path('oauth/callback/', views.google_callback, name='google_callback'),
    path('dashboard/', views.home, name='home'),
    path('docs/', views.docs, name='docs'),
    path('register/', views.confirm_schedule, name='register'),
    path('<int:task_id>/', views.details, name='details'),
    path('edit/<int:task_id>/', views.edit_schedule, name='edit'),
    path('delete/<int:task_id>/', views.delete_schedule, name='delete'),
]
