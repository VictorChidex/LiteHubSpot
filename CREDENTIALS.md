# Valid Authentication Credentials

## Seeded Test User

Use these credentials to test the API with a pre-populated database (5 sample todos already created):

**Username:** `seeduser1766500569`  
**Email:** `seed1766500569@example.com`  
**Password:** `seedpass`  
**Auth Token:** `97a66cac068d8a9d1a92cd9253c0ed6da96ce525`

## Quick Start: Test the API

### 1. List todos (GET /api/todos/)
```bash
curl -H "Authorization: Token 97a66cac068d8a9d1a92cd9253c0ed6da96ce525" \
  http://127.0.0.1:8001/api/todos/
```

### 2. Create a new todo (POST /api/todos/)
```bash
curl -X POST http://127.0.0.1:8001/api/todos/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token 97a66cac068d8a9d1a92cd9253c0ed6da96ce525" \
  -d '{"title":"My New Task","description":"Task description","priority":"high"}'
```

### 3. Get user profile (GET /api/auth/profile/)
```bash
curl -H "Authorization: Token 97a66cac068d8a9d1a92cd9253c0ed6da96ce525" \
  http://127.0.0.1:8001/api/auth/profile/
```

## Create a New User

If you want to create your own account:

### Signup (POST /api/auth/signup/)
```bash
curl -X POST http://127.0.0.1:8001/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email":"newuser@example.com",
    "username":"newuser",
    "password":"mypassword123"
  }'
```

Response will include a new token for your account.

### Login (POST /api/auth/login/)
```bash
curl -X POST http://127.0.0.1:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "identifier":"newuser",
    "password":"mypassword123"
  }'
```

## Important Notes

- **Token Format:** Always include the Authorization header as: `Authorization: Token <your_token>`
- **Database:** Todos are persisted in `/workspaces/LiteHubSpot/backend/db.sqlite3`
- **Port:** Backend API runs on `http://127.0.0.1:8001`
- **Frontend:** Runs on `http://127.0.0.1:8000` and uses the backend API automatically
