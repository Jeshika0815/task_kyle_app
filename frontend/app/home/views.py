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


# Logout
def logout(request):
    request.session.flush()
    return redirect('visitor')


# Login
def login(request):
    if request.method == 'POST':
        response = requests.post(
            f"{API_ENDPOINT}/auth/login",
            data={"username": request.POST.get('email', ''), "password": request.POST.get('password', '')},
        )
        if response.status_code == 200:
            request.session['token'] = response.json().get('access_token')
            return redirect('home')
        return render(request, 'login.html', {'error': 'ログインに失敗しました.', 'google_auth_url': f"{API_ENDPOINT}/auth/google"})
    return render(request, 'login.html', {'google_auth_url': f"{API_ENDPOINT}/auth/google"})


# Google OAuth callback: the backend's /auth/google redirects the browser here
# (via ENDPOINT) with ?code=..., we exchange it for a token server-side and
# store it in the Django session, same as a normal login.
def google_callback(request):
    code = request.GET.get('code')
    if not code:
        return render(request, 'login.html', {
            'error': 'Google認証がキャンセルされました.',
            'google_auth_url': f"{API_ENDPOINT}/auth/google",
        })
    response = requests.get(f"{API_ENDPOINT}/auth/google", params={"code": code})
    if response.status_code == 200:
        request.session['token'] = response.json().get('access_token')
        return redirect('home')
    return render(request, 'login.html', {
        'error': 'Google認証に失敗しました.',
        'google_auth_url': f"{API_ENDPOINT}/auth/google",
    })


# Signin(register)
def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        response = requests.post(
            f"{API_ENDPOINT}/auth/register",
            json={"user": {"id": 0, "email": email, "password": password, "confirm_oauth": False}},
        )
        if response.status_code != 200:
            return render(request, 'signin.html', {'error': '登録に失敗しました.', 'google_auth_url': f"{API_ENDPOINT}/auth/google"})

        # Registration doesn't issue a token, so log the new user in right away.
        login_response = requests.post(
            f"{API_ENDPOINT}/auth/login",
            data={"username": email, "password": password},
        )
        if login_response.status_code == 200:
            request.session['token'] = login_response.json().get('access_token')
            return redirect('home')
        return redirect('login')
    return render(request, 'signin.html', {'google_auth_url': f"{API_ENDPOINT}/auth/google"})


# Documentation
def docs(request):
    return render(request, 'help.html')


# Authenticated user
def home(request):
    token = token_verification(request)
    if not isinstance(token, str):
        return token
    try:
        response = requests.get(f"{API_ENDPOINT}/task/", headers=_auth_header(token))
        response.raise_for_status()
        return render(request, 'home.html', {'tasks': response.json()})
    except requests.RequestException as e:
        return render(request, 'home.html', {'error': str(e), 'tasks': []})


# Schedule registration process: free-text prompt -> analyze -> confirm -> create
def confirm_schedule(request):
    token = token_verification(request)
    if not isinstance(token, str):
        return token

    # Stage 2: the user confirmed/edited the analyzed plan -> create it
    if request.method == 'POST' and request.POST.get('stage') == 'confirm':
        payload = _plan_payload_from_post(request.POST)
        response = requests.post(f"{API_ENDPOINT}/task/add", json=payload, headers=_auth_header(token))
        if response.status_code == 200:
            return redirect('home')
        return render(request, 'confirm_schedule.html', {
            'task': payload,
            'error': f'予定の登録に失敗しました: {response.text}',
        })

    # Stage 1: analyze a free-text prompt (or start a blank manual entry)
    prompt = ''
    if request.method == 'POST':
        form = PromptForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
    else:
        prompt = request.GET.get('prompt', '')

    task = _blank_plan()
    if prompt:
        response = requests.post(
            f"{API_ENDPOINT}/prompt_ctl/prompt_analyze",
            params={"prompt": prompt},
            headers=_auth_header(token),
        )
        if response.status_code == 200:
            task = response.json()
        else:
            return render(request, 'home.html', {'error': '入力の解析に失敗しました.', 'tasks': []})
    return render(request, 'confirm_schedule.html', {'task': task})


# Detail of a task
def details(request, task_id):
    token = token_verification(request)
    if not isinstance(token, str):
        return token
    response = requests.get(f"{API_ENDPOINT}/task/view_task", params={"task_id": task_id}, headers=_auth_header(token))
    if response.status_code != 200:
        return redirect('home')
    return render(request, 'detail_schedule.html', {'task': response.json()})


# Schedule editing
def edit_schedule(request, task_id):
    token = token_verification(request)
    if not isinstance(token, str):
        return token

    if request.method == 'POST':
        payload = _plan_payload_from_post(request.POST)
        payload['id'] = task_id
        response = requests.post(f"{API_ENDPOINT}/task/update", json=payload, headers=_auth_header(token))
        if response.status_code == 200:
            return redirect('details', task_id=task_id)
        return render(request, 'edit_schedule.html', {
            'task': payload,
            'error': f'更新に失敗しました: {response.text}',
        })

    response = requests.get(f"{API_ENDPOINT}/task/view_task", params={"task_id": task_id}, headers=_auth_header(token))
    if response.status_code != 200:
        return redirect('home')
    return render(request, 'edit_schedule.html', {'task': response.json()})


# Delete Schedule
def delete_schedule(request, task_id):
    token = token_verification(request)
    if not isinstance(token, str):
        return token

    if request.method == 'POST':
        payload = _plan_payload_from_post(request.POST)
        payload['id'] = task_id
        try:
            response = requests.delete(f"{API_ENDPOINT}/task/delete", json=payload, headers=_auth_header(token))
            response.raise_for_status()
            return redirect('home')
        except requests.RequestException as e:
            return render(request, 'delete_schedule.html', {'task': payload, 'error': str(e)})

    response = requests.get(f"{API_ENDPOINT}/task/view_task", params={"task_id": task_id}, headers=_auth_header(token))
    if response.status_code != 200:
        return redirect('home')
    return render(request, 'delete_schedule.html', {'task': response.json()})


# Not route
# Verifies the token and returns it, or a redirect response to login
def token_verification(request):
    token = request.session.get('token')
    if not token:
        return redirect('login')
    return token


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _blank_plan():
    return {
        'plan_name': '',
        'date': {'start_date': None, 'finish_date': None},
        'time': {'start_time': None, 'finish_time': None},
        'alarm': False,
        'repeats': None,
        'tags': [],
        'location': None,
        'url': None,
        'memo': None,
    }


# Builds an EventCreate/Plans-shaped payload out of the flat fields the templates submit
def _plan_payload_from_post(post):
    tags = [t.strip() for t in post.get('tags', '').split(',') if t.strip()]
    return {
        'plan_name': post.get('plan_name', ''),
        'date': {
            'start_date': post.get('start_date') or None,
            'finish_date': post.get('finish_date') or None,
        },
        'time': {
            'start_time': post.get('start_time') or None,
            'finish_time': post.get('finish_time') or None,
        },
        'alarm': post.get('alarm') == 'on',
        'repeats': post.get('repeats') or None,
        'tags': tags,
        'location': post.get('location') or None,
        'url': post.get('url') or None,
        'memo': post.get('memo') or None,
    }
