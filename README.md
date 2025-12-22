# LiteHubSpot

LiteHubSpot is a lightweight, Django-based Todo application designed to demonstrate a clean, interactive user experience with a **mocked service layer** backend, featuring a modern UI inspired by professional task management tools.

## 🚀 Features

- **User Authentication**: Sign up and Log in functionality (session-based).
- **Todo Management**:
    - Create new tasks with due dates and descriptions.
    - View a list of your tasks in a clean, card-based layout.
    - **Interactive Actions**: Mark tasks as resolved/unresolved, Edit details, and Delete tasks.
- **Modern UI**: Professional interface with sidebar navigation, inspired by tools like ClickUp, Notion, and Monday.com.
- **Mock Backend**: Uses an in-memory `MockBackendService` to simulate a database.
- **Responsive Design**: Built with Tailwind CSS for a modern, clean look.

## 🛠 Tech Stack

- **Framework**: Django 5.0+
- **Database**: None (In-Memory Python Dictionaries)
- **Frontend**: Django Templates + Tailwind CSS + Font Awesome icons
- **Testing**: `unittest` with Django's `Client`

## 📦 Installation & Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd LiteHubSpot
   ```

2. **Install Dependencies**:
   ```bash
   pip install django
   ```

3. **Run the Server**:
   ```bash
   cd frontend
   python3 manage.py runserver
   ```
   *Note: You do not need to run `makemigrations` or `migrate` because the app uses a mock in-memory store and bypasses the default database.*

4. **Access the App**:
   Open your browser and navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).

## 🧪 Running Tests

The application comes with a suite of unit and integration tests covering the mock service and views.

```bash
cd frontend
python3 manage.py test todos
```

## ⚠️ Important Note

**Data Persistence**: Since this application uses an **in-memory mock backend** (`todos.services.MockBackendService`), **all data (users and todos) will be lost when the server is restarted.** This is by design for this specific demonstration.

## 📂 Project Structure

- `config/`: Project configuration (`settings.py`, `urls.py`).
- `todos/`: Main application.
    - `services.py`: The mock backend logic.
    - `views.py`: Controllers handling requests.
    - `tests.py`: Test suite.
- `templates/`: HTML templates.
- `static/`: CSS files.