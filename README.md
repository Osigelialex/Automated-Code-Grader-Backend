# CheckMate

CheckMate is an advanced automated grading system for the assessment of programming assignments. It combines automated test case evaluation with LLM-powered feedback to provide a comprehensive and efficient grading solution for programming courses.

## Key Features

### Automated Grading:
  - Evaluate student submissions using pre-defined test cases.
  - Provide immediate feedback on the correctness of the code.

### LLM-powered Feedback:
  - Integrate with LLMs to generate comprehensive feedback reports, identifying potential issues and suggesting improvements.

### Assignment Management:
  - Create and manage programming assignments.
  - Specify assignment details, deadlines, and test cases.
  - Track student submissions and grading status.

### Course Management:
  - Organize assignments within courses.
  - Manage student enrollment for courses.

### User Management:
  - Create separate accounts for instructors (lecturers) and students.
  - Implement role-based access control for different functionalities.

## Caching and Rate Limiting:
  - Caches submission results and LLM feedback to improve performance.
  - Rate limiting is applied to prevent misuse.

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis

### Installation

1. Clone the repository
```bash
git clone https://github.com/Osigelialex/checkmate-backend.git
cd checkmate-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. **Install dependencies**
```
pip install -r requirements.txt
```

4. **Setup environment variables**
```
cp .env.example .env
```

5. **Run migrations**
```
python manage.py migrate
```

6. **Start the server**
```
python manage.py runserver
```

**Environment Variables**
```bash
SECRET_KEY=your-django-secret-key
DEBUG=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=
DB_USER=
DB_HOST=
DB_PORT=5432
DB_PASSWORD=
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_PORT=
BASE_URL=http://localhost:8000
X_RAPIDAPI_KEY=Your judge0 rapid API key
X_RAPIDAPI_HOST=your judge0 rapid API host
```

5. **API documentation**
To visit the API documentation, go to http://localhost:8000
