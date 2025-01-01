# CheckMate: Automated Grader for Programming Assignments

CheckMate is an advanced automated grading system designed to streamline the assessment of programming assignments. By combining automated test-case evaluation with Large Language Model (LLM)-powered personalized feedback.

## Features

### **Automated Grading**
- **Test-Case-Based Evaluation**: Automatically runs and validates student code against a comprehensive suite of test cases for objective scoring.
- **LLM Integration**:
  - Provides personalized feedback on code quality, readability, and adherence to best practices.
  - Suggests improvements and alternative approaches to coding challenges.
- **Batch Processing**: Handles multiple submissions simultaneously, ensuring timely feedback for large classes.

### **Course Management**
- **Course Creation and Enrollment**: Enables lecturers to create and manage courses with ease.
- **Customizable Assignments**:
  - Define unique test cases and grading rubrics for each assignment.
  - Flexible deadline management and automatic handling of late submissions.

### **Assignment Management**
- **Student Submission Interface**:
  - Built-in code editor with syntax highlighting and linting.
  - Real-time feedback on code style and potential errors.
- **Version Control**: Tracks submission history and allows students to resubmit assignments before deadlines.

### **User Management**
- **Role-Based Access Control**:
  - Students: Submit assignments and view feedback.
  - Lecturers: Create courses, manage assignments, and review grading.
- **Authentication and Authorization**: Secure login system with session management.
- **User Profiles**: Tracks user progress, assignment history, and feedback.

---

## Technology Stack

### **Backend**
- **Framework**: Django and Django REST Framework (DRF) for robust API development.
- **Database**: PostgreSQL for reliable and scalable data storage.
- **Caching**: Redis to improve performance and reduce repeated LLM queries.

### **Frontend**
- **Framework**: React/Next.js for a dynamic and responsive user interface.
- **Styling**: TailwindCSS for modern, customizable, and responsive designs.
- **Code Editor**: Monaco Editor for an IDE-like experience within the browser.
- **API Communication**: Axios for seamless interaction with backend APIs.

### **LLM Integration**
- **API**: Gemini API for cutting-edge natural language processing.
- **Custom Prompt Engineering**:
  - Tailored prompts to generate meaningful and educational feedback.
  - Optimized for accuracy and context-relevance.
- **Feedback Optimization**:
  - Implements feedback caching to avoid redundant LLM calls.
  - Rate limiting to ensure API usage efficiency.

---

## Installation and Setup

1. **Clone the repository**
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
