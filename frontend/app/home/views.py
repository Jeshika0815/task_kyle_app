# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.conf import settings
from .forms import PromptForm

import requests

# get API endpoint
API_ENDPOINT = settings.API_ENDPOINT

# Un authenticated user
def welcome(request):
    return render(request, 'visitor.html')

# Login
def login(request):
    if request.method == 'POST':
        response = requests.post(f"{API_ENDPOINT}/auth/login", json={"username": request.POST['username'], "password": request.POST['password']})
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
            return redirect('login')
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
        response = requests.get(f"{API_ENDPOINT}/tasks/", headers={"Authorization": f"Bearer {token}"})
        return render(request, 'home.html',{'tasks': response.json()})
    except requests.RequestException as e:
        return render(request, 'home.html', {'error': str(e)})
    if request.method == 'POST':
        prompt = PromptForm(request.POST)
        if prompt.is_valid():
            return redirect('register', prompt=prompt.cleaned_data['input'])
        else:
            return render(request, 'home.html', {'prompt': prompt.cleaned_data['prompt']})
    return render(request, 'home.html')

# Schedule registration process
def confirm_schedule(request):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    response_tasks = requests.post(f"{API_ENDPOINT}/prompt_ctl/ptompt_analyze", headers={"Authorization": f"Bearer {token}"}, data = request.POST)
    tasks = []
    for i in response_tasks.json():
        tasks.append(i)

    if request.method == 'POST':
        res = requests.post(f"{API_ENDPOINT}/tasks/add", headers={"Authorization": f"Bearer {token}"}, data=request.POST)
        if res.status_code == 200:
            return redirect('home')
        else:
            return render(request, 'home.html', {'error': f'Failed to add task: {res.text}'})
    return render(request, 'confirm_schedule.html', {'tasks': tasks})

# Detail of a task
def details(request, task_id):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    response = requests.get(f"{API_ENDPOINT}/tasks/{task_id}/", headers={"Authorization": f"Bearer {token}"})
    return render(request, 'detail_schedule.html', {'task': response.json()})

# Schedule editing
def edit_schedule(request, task_id):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    response = requests.get(f"{API_ENDPOINT}/tasks/edit/{task_id}/", headers={"Authorization": f"Bearer {token}"})
    return render(request, 'edit_schedule.html', {'task': response.json()})

# Delete Schedule
def delete_schedule(request, task_id):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    try:
        response = requests.delete(f"{API_ENDPOINT}/tasks/{task_id}/", headers={"Authorization": f"Bearer {token}"})
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
