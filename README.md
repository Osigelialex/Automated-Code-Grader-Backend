# Automated Grader for Programming Assignments

CheckMate is an automated grading system for programming assignments that combines automated test-case evaluation with LLM-powered personalized feedback for programming assignments.

## Features

**Automated Grading**
- Test-case-based evaluation for objective assessment
- LLM integration for personalized feedback on code quality, style, and improvements
- Batch processing of submissions
  
**Course Management**
- Course creation and enrollment management
- Assignment creation with customizable test cases
- Deadline management and late submission handling
  
**Assignment Management**
- Student submission interface with code editor
- Submission history and version control
  
**User Management**
- Role-based access control (Student/Lecturer)
- Authentication and authorization
- User profiles and progress tracking

## Technology Stack

### Backend
- Django
- Django REST Framework
- PostgreSQL
- Celery (for async task processing)
- Redis (for caching)

### Frontend
- React/Next.js
- TailwindCSS
- Monaco (for code editor)
- Axios (for API calls)

### LLM Integration
- Gemini API integration
- Custom prompt engineering for educational feedback
- Feedback caching and rate limiting

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/Osigelialex/codegradr.git
cd codegradr
```

2. **Backend setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration
# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

3. **Frontend setup**
Visit the frontend repository here 

4. **Environment Variables**
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
