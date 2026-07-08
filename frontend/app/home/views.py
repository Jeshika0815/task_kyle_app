# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.conf import settings
import requests
import os

# routes(home(show tasks(list)), calender(later), confirm_schedule, edit, delete, help)

# get API endpoint
API_ENDPOINT = settings.API_ENDPOINT

# Un authenticated user
def welcome(request):
    return render(request, 'visitor.html')

# Login
def login(request):
    if request.method == 'POST':
        response = requests.post(f"{API_ENDPOINT}/auth/login", json={"email": request.POST['email'], "password": request.POST['password']})
        if response.status_code == 200:
            token = response.json().get('token')
            request.session['token'] = token
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'ログインに失敗しました.'})
    return render(request, 'login.html')

# Signin(register)
def signin(request):
    if request.method == 'POST':
        response = requests.post(f"{API_ENDPOINT}/auth/register", json={"email": request.POST['email'], "password": request.POST['password']})
        if response.status_code == 200:
            token = response.json().get('token')
            request.session['token'] = token
            return redirect('home')
        else:
            return render(request, 'signin.html', {'error': '登録に失敗しました.'})
    return render(request, 'signin.html')

# Documentation
def docs(request):
    return render(request, 'help.html')

# Authenticated user
def home(request, prompt):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    try:
        response = requests.get(f"{API_ENDPOINT}/", headers={"Authorization": f"Bearer {token}"})
        return render(request, 'home.html', {'user': request.user, 'tasks': response.json()})
    except requests.RequestException as e:
        return render(request, 'home.html', {'error': str(e)})

# Schedule registration process
def confirm_schedule(request):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    response_tasks = requests.get(f"{API_ENDPOINT}/ptompt_analyze", )
    return render(request, 'confirm_schedule.html')

# Schedule editing
def edit_schedule(request):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    return render(request, 'edit_schedule.html')

# Delete Schedule
def delete_schedule(request):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    try:
        response = requests.delete(f"{API_ENDPOINT}/", headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return redirect('home')
    except requests.RequestException as e:
        return render(request, 'delete_schedule.html', {'error': str(e)})
    return render(request, 'delete_schedule.html')

# Not route
# Verifies the token and returns or redirects to login
def token_verification(request):
    token = request.session.get('token')
    if not token:
        return redirect('login')
    return token
