# views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model
import os

# routes(home(show tasks(list)), calender(later), confirm_schedule, edit, delete, help)

# Un authenticated user
def welcome(request):
    return render(request, 'visitor.html')

# Documentation
def docs(request):
    return render(request, 'help.html')

# Authenticated user
def home(request):
    return render(request, 'home.html', {'user': request.user})

# Schedule registration process
def confirm_schedule(request):
    return render(request, 'confirm_schedule.html')

# Schedule editing
def edit_schedule(request):
    return render(request, 'edit_schedule.html')

# Delete Schedule
def delete_schedule(request):
    return render(request, 'delete_schedule.html')
