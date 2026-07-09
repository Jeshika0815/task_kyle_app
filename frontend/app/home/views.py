# views.py
from django.shortcuts import render, redirect
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
        response = requests.post(
            f"{API_ENDPOINT}/auth/login",
            data={"username": request.POST['email'], "password": request.POST['password']},
        )
        if response.status_code == 200:
            token = response.json().get('access_token')
            request.session['token'] = token
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'ログインに失敗しました.'})
    return render(request, 'login.html')

# Signin(register)
def signin(request):
    if request.method == 'POST':
        response = requests.post(
            f"{API_ENDPOINT}/auth/register",
            json={"email": request.POST['email'], "password": request.POST['password']},
        )
        if response.status_code == 200:
            token = response.json().get('access_token')
            request.session['token'] = token
            return redirect('home')
        else:
            return render(request, 'signin.html', {'error': '登録に失敗しました.'})
    return render(request, 'signin.html')

# Documentation
def docs(request):
    return render(request, 'help.html')

# Authenticated user
def home(request):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    try:
        response = requests.get(f"{API_ENDPOINT}/task/", headers={"Authorization": f"Bearer {token}"})
        return render(request, 'home.html', {'tasks': response.json()})
    except requests.RequestException as e:
        return render(request, 'home.html', {'error': str(e)})

# Schedule registration process
def confirm_schedule(request):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == 'POST' and request.POST.get('stage') == 'confirm':
        tags = [t.strip() for t in request.POST.get('tags', '').split(',') if t.strip()]
        payload = {
            "plan_name": request.POST['plan_name'],
            "start_date": request.POST['start_date'],
            "finish_date": request.POST.get('finish_date') or None,
            "start_time": request.POST['start_time'],
            "finish_time": request.POST.get('finish_time') or None,
            "alarm": bool(request.POST.get('alarm')),
            "repeats": request.POST.get('repeats') or None,
            "tags": tags,
            "location": request.POST.get('location') or None,
            "url": request.POST.get('url') or None,
            "departure": bool(request.POST.get('departure')),
            "departure_time": request.POST.get('departure_time') or None,
            "memo": request.POST.get('memo') or None,
        }
        res = requests.post(f"{API_ENDPOINT}/task/add", headers=headers, json=payload)
        if res.status_code == 200:
            return redirect('home')
        else:
            return render(request, 'home.html', {'error': f'Failed to add task: {res.text}'})

    if request.method == 'POST':
        prompt_form = PromptForm(request.POST)
        if not prompt_form.is_valid():
            return render(request, 'confirm_schedule.html', {'plan': None, 'form': prompt_form})

        response_tasks = requests.post(
            f"{API_ENDPOINT}/prompt_ctl/prompt_analyze",
            headers=headers,
            data={"prompt": prompt_form.cleaned_data['prompt']},
        )
        plan = response_tasks.json() if response_tasks.status_code == 200 else {}
        return render(request, 'confirm_schedule.html', {'plan': plan, 'form': PromptForm()})

    return render(request, 'confirm_schedule.html', {'plan': None, 'form': PromptForm()})

# Detail of a task
def details(request, task_id):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    response = requests.get(
        f"{API_ENDPOINT}/task/view_task",
        params={"task_id": task_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    return render(request, 'detail_schedule.html', {'task': response.json()})

# Schedule editing
def edit_schedule(request, task_id):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == 'POST':
        tags = [t.strip() for t in request.POST.get('tags', '').split(',') if t.strip()]
        payload = {
            "id": task_id,
            "plan_name": request.POST['plan_name'],
            "start_date": request.POST['start_date'],
            "finish_date": request.POST.get('finish_date') or None,
            "start_time": request.POST['start_time'],
            "finish_time": request.POST.get('finish_time') or None,
            "alarm": bool(request.POST.get('alarm')),
            "repeats": request.POST.get('repeats') or None,
            "tags": tags,
            "location": request.POST.get('location') or None,
            "url": request.POST.get('url') or None,
            "departure": bool(request.POST.get('departure')),
            "departure_time": request.POST.get('departure_time') or None,
            "memo": request.POST.get('memo') or None,
        }
        res = requests.post(f"{API_ENDPOINT}/task/update", headers=headers, json=payload)
        if res.status_code == 200:
            return redirect('details', task_id=task_id)
        else:
            return render(request, 'edit_schedule.html', {'error': f'Failed to update task: {res.text}'})

    response = requests.get(f"{API_ENDPOINT}/task/view_task", params={"task_id": task_id}, headers=headers)
    return render(request, 'edit_schedule.html', {'task': response.json()})

# Delete Schedule
def delete_schedule(request, task_id):
    token_or_redirect = token_verification(request)
    if not isinstance(token_or_redirect, str):
        return token_or_redirect
    token = token_or_redirect
    try:
        response = requests.delete(
            f"{API_ENDPOINT}/task/delete",
            params={"task_id": task_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return redirect('home')
    except requests.RequestException as e:
        return render(request, 'delete_schedule.html', {'error': str(e)})

# Not route
# Verifies the token and returns or redirects to login
def token_verification(request):
    token = request.session.get('token')
    if not token:
        return redirect('login')
    return token
