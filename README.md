# LiteHubSpot

LiteHubSpot is a lightweight, Django-based Todo application designed to demonstrate a clean, interactive user experience with a **mocked service layer** backend, featuring a modern UI inspired by professional task management tools.

## 🚀 Features

- **User Authentication**: Sign up and Log in functionality (session-based).
- **Todo Management**:
    - Create new tasks with due dates, descriptions, priorities, and statuses.
    - View tasks in List or Board view.
    - **Interactive Actions**: Mark tasks as resolved/unresolved, Edit details, and Delete tasks.
    - **Priority Levels**: Low, Normal, High, Urgent with color-coded badges and flag icons for visual clarity.
    - **Status Workflow**: To Do, In Progress, Done with board columns.
- **Modern UI**: Professional interface with sidebar navigation, inspired by tools like ClickUp, Notion, and Monday.com.
- **Mock Backend**: Uses an in-memory `MockBackendService` to simulate a database.
- **REST API**: Django REST Framework API with mock database for backend operations.
- **Responsive Design**: Built with Tailwind CSS for a modern, clean look.

## 🛠 Tech Stack

- **Framework**: Django 5.0+ with Django REST Framework
- **Database**: None (In-Memory Python Dictionaries for both frontend and API)
- **Frontend**: Django Templates + Tailwind CSS + Font Awesome icons
- **API**: Django REST Framework with token authentication (mock implementation)
- **Testing**: `unittest` with Django's `Client`

## 📦 Installation & Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd LiteHubSpot
   ```

2. **Install Dependencies**:
   ```bash
   # For frontend
   pip install django

   # For backend API (using uv as per AGENTS.md)
   cd backend
   uv sync
   ```

3. **Run the Frontend Server**:
   ```bash
   cd frontend
   python3 manage.py runserver
   ```
   *Note: You do not need to run `makemigrations` or `migrate` because the app uses a mock in-memory store and bypasses the default database.*

4. **Run the Backend API Server** (optional, for API testing):
   ```bash
   cd backend
   uv run python manage.py runserver 8001
   ```

5. **Access the Apps**:
   - Frontend: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - API: [http://127.0.0.1:8001](http://127.0.0.1:8001) (if running)

## 🔌 API Endpoints

The Django REST API provides the following endpoints:

### Authentication
- `POST /api/auth/signup/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get current user profile

### Todos
- `GET /api/todos/` - List all todos for current user
- `POST /api/todos/` - Create a new todo
- `GET /api/todos/{id}/` - Get specific todo
- `PUT /api/todos/{id}/` - Update todo
- `DELETE /api/todos/{id}/` - Delete todo
- `POST /api/todos/{id}/resolve/` - Toggle todo resolution
- `POST /api/todos/{id}/status/` - Update todo status

**Headers**: Include `X-User-ID: default-admin-id` for mock authentication.

## 🧪 Running Tests

The application comes with a comprehensive suite of **23 unit and integration tests** covering authentication, CRUD operations, priority/status workflows, user isolation, and UI functionality.

```bash
cd frontend
python3 manage.py test todos
```

## ⚠️ Important Note

**Data Persistence**: Since this application uses an **in-memory mock backend** (`todos.services.MockBackendService` and `api.mock_db.MockDatabase`), **all data (users and todos) will be lost when the server is restarted.** This is by design for this specific demonstration.

## 📂 Project Structure

- `frontend/`: Django frontend application
  - `config/`: Project configuration (`settings.py`, `urls.py`)
  - `todos/`: Main application with mock backend service
  - `templates/`: HTML templates
  - `static/`: CSS files
- `backend/`: Django REST API
  - `litehubspot_api/`: API project configuration
  - `api/`: API application with mock database service
    - `mock_db.py`: In-memory database implementation
    - `views.py`: API endpoint views
    - `serializers.py`: Data serializers
    - `urls.py`: API routing
