"""Frontend service layer that talks to the backend API.

This replaces the previous in-memory mock service and proxies calls to
the backend running at `FRONTEND_API_URL` (env var) or default
http://127.0.0.1:8001/api/
"""
import os
import requests
from urllib.parse import urljoin

API_BASE = os.environ.get('FRONTEND_API_URL', 'http://127.0.0.1:8001/api/')

def _build_headers(token=None):
	headers = {'Content-Type': 'application/json'}
	if token:
		headers['Authorization'] = f'Token {token}'
	return headers

def register_user(email, username, password):
	url = urljoin(API_BASE, 'auth/signup/')
	payload = {"email": email, "username": username, "password": password}
	r = requests.post(url, json=payload, headers=_build_headers())
	r.raise_for_status()
	return r.json()

def authenticate_user(identifier, password):
	url = urljoin(API_BASE, 'auth/login/')
	payload = {"identifier": identifier, "password": password}
	r = requests.post(url, json=payload, headers=_build_headers())
	if r.status_code != 200:
		return None
	return r.json()

def get_user_by_token(token):
	url = urljoin(API_BASE, 'auth/profile/')
	r = requests.get(url, headers=_build_headers(token))
	r.raise_for_status()
	return r.json()

def get_todos(token):
	url = urljoin(API_BASE, 'todos/')
	r = requests.get(url, headers=_build_headers(token))
	r.raise_for_status()
	return r.json()

def get_todo(todo_id, token):
	url = urljoin(API_BASE, f'todos/{todo_id}/')
	r = requests.get(url, headers=_build_headers(token))
	if r.status_code == 404:
		return None
	r.raise_for_status()
	return r.json()

def create_todo(user_id, title, due_date=None, description="", priority="normal", status="to_do", token=None):
	url = urljoin(API_BASE, 'todos/')
	payload = {"title": title, "description": description, "due_date": due_date, "priority": priority, "status": status}
	r = requests.post(url, json=payload, headers=_build_headers(token))
	r.raise_for_status()
	return r.json()

def update_todo(todo_id, **kwargs):
	token = kwargs.pop('token', None)
	url = urljoin(API_BASE, f'todos/{todo_id}/')
	r = requests.put(url, json=kwargs, headers=_build_headers(token))
	r.raise_for_status()
	return r.json()

def delete_todo(todo_id, token=None):
	url = urljoin(API_BASE, f'todos/{todo_id}/')
	r = requests.delete(url, headers=_build_headers(token))
	return r.status_code == 204

from datetime import datetime
import uuid
