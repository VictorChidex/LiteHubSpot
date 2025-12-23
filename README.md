# LiteHubSpot

LiteHubSpot is a lightweight, Django-based Todo application with a persistent backend API, featuring a modern UI inspired by professional task management tools. It includes both a Django frontend and a Django REST Framework API with SQLAlchemy-backed persistence.

## 🚀 Features

- **User Authentication**: Token-based API authentication with user registration and login.
- **Todo Management**:
    - Create new tasks with due dates, descriptions, priorities, and statuses.
    - View tasks in List or Board view via the frontend UI.
    - **Interactive Actions**: Mark tasks as resolved/unresolved, Edit details, and Delete tasks.
    - **Priority Levels**: Low, Normal, High, Urgent with color-coded badges and flag icons for visual clarity.
    - **Status Workflow**: To Do, In Progress, Done with board columns.
- **Modern UI**: Professional frontend with sidebar navigation, inspired by tools like ClickUp, Notion, and Monday.com.
- **REST API**: Django REST Framework with token-based authentication and SQLAlchemy persistence.
- **Persistent Database**: SQLAlchemy ORM with SQLite (local dev) and optional PostgreSQL support.
- **Responsive Design**: Built with Tailwind CSS for a modern, clean look.

## 🛠 Tech Stack

- **Framework**: Django 6.0 with Django REST Framework
- **Database**: SQLAlchemy with SQLite (default) or PostgreSQL (via `DATABASE_URL` env var)
- **Frontend**: Django Templates + Tailwind CSS + Font Awesome icons
- **API**: Django REST Framework with Token Authentication
- **Concurrency**: npm `concurrently` for running both servers together
- **Dependency Management**: `uv` for backend Python packages

## 📦 Installation & Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd LiteHubSpot
   ```

2. **Install Dependencies**:
   ```bash
   # Install npm dependencies (including concurrently)
   npm install --no-audit --no-fund

   # Install backend Python dependencies
   cd backend
   uv sync
   cd ..
   ```

3. **Run Both Servers Concurrently** (recommended):
   ```bash
   npm run start
   ```
   This starts:
   - Frontend: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Backend API: [http://127.0.0.1:8001](http://127.0.0.1:8001)

4. **Or Run Servers Separately**:
   ```bash
   # Terminal 1: Frontend
   cd frontend
   python3 manage.py runserver

   # Terminal 2: Backend
   cd backend
   python3 manage.py runserver 8001
   ```

5. **Access the Applications**:
   - **Frontend UI**: [http://127.0.0.1:8000](http://127.0.0.1:8000) (signup/login to use)
   - **API Root**: [http://127.0.0.1:8001/api/](http://127.0.0.1:8001/api/)
   - **Credentials**: See [CREDENTIALS.md](./CREDENTIALS.md) for pre-seeded test user

## 🔌 API Endpoints

The Django REST API provides the following endpoints with **Token Authentication**:

### Authentication
- `POST /api/auth/signup/` - User registration
- `POST /api/auth/login/` - User login (returns token)
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get current user profile (requires token)

### Todos
- `GET /api/todos/` - List all todos for current user (requires token)
- `POST /api/todos/` - Create a new todo (requires token)
- `GET /api/todos/{uuid}/` - Get specific todo (requires token)
- `PUT /api/todos/{uuid}/` - Update todo (requires token)
- `DELETE /api/todos/{uuid}/` - Delete todo (requires token)
- `POST /api/todos/{uuid}/resolve/` - Toggle todo resolution (requires token)
- `POST /api/todos/{uuid}/status/` - Update todo status (requires token)

**Authentication**: Include the token in the request header:
```bash
Authorization: Token <your_token>
```

**Example**:
```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" http://127.0.0.1:8001/api/todos/
```

For pre-seeded credentials and more examples, see [CREDENTIALS.md](./CREDENTIALS.md).

## 🧪 Running Tests

```bash
cd frontend
python3 manage.py test todos
```

## 💾 Database

- **Default**: SQLite at `/workspaces/LiteHubSpot/backend/db.sqlite3`
- **Persistent**: Data persists across server restarts
- **PostgreSQL** (optional): Set `DATABASE_URL` environment variable to use PostgreSQL instead:
  ```bash
  export DATABASE_URL="postgresql://user:password@localhost/litehubspot"
  python manage.py runserver 8001
  ```

## 🔐 Authentication Credentials

A pre-seeded test user is available immediately after server startup:

- **Username**: `seeduser1766500569`
- **Password**: `seedpass`
- **Token**: `97a66cac068d8a9d1a92cd9253c0ed6da96ce525`
- **Pre-loaded**: 5 sample todos

See [CREDENTIALS.md](./CREDENTIALS.md) for full details and API usage examples.

## 📂 Project Structure

```
LiteHubSpot/
├── backend/                          # Django REST API
│   ├── litehubspot_api/             # API project config
│   ├── api/                         # API app
│   │   ├── views.py                 # API endpoints
│   │   ├── serializers.py           # DRF serializers
│   │   ├── sqlalchemy_db.py         # SQLAlchemy engine & session
│   │   ├── sql_models.py            # SQLAlchemy Todo model
│   │   ├── urls.py                  # API routing
│   │   └── migrations/              # Django migrations
│   ├── manage.py
│   ├── db.sqlite3                   # SQLite database
│   └── pyproject.toml               # uv dependencies
├── frontend/                         # Django Frontend
│   ├── config/                      # Project configuration
│   ├── todos/                       # Frontend app
│   │   ├── views.py                 # Django views
│   │   ├── services.py              # HTTP API client (calls backend)
│   │   ├── urls.py                  # Frontend routing
│   │   └── migrations/
│   ├── templates/                   # HTML templates
│   ├── static/                      # CSS & assets
│   ├── manage.py
│   └── db.sqlite3
├── package.json                      # npm scripts for concurrently
├── CREDENTIALS.md                    # Pre-seeded test user credentials
└── README.md
```
