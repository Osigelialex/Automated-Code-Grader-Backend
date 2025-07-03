
<p align="center">
  <img src="https://img.shields.io/badge/Django-5.1.2-green?style=flat-square&logo=django" alt="Django">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-blue?style=flat-square&logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-Cache-red?style=flat-square&logo=redis" alt="Redis">
</p>

# CheckMate

> **Automated, AI-powered grading for programming assignments.**
>
> _Accelerate assessment. Empower learning. Deliver instant, actionable feedback._

CheckMate is a robust backend system for automated grading of programming assignments. It combines test case evaluation, LLM-powered feedback, and modern course management to streamline the grading process for instructors and enhance the learning experience for students.

---

## 🚀 Features

- **Automated Grading:**
  - Instantly evaluate code submissions against instructor-defined test cases.
  - Supports multiple programming languages via Judge0 API.
  - Immediate, objective scoring for every submission.

- **AI-Powered Feedback:**
  - Uses LLMs (e.g., Gemini) to generate personalized, constructive feedback for students.
  - Feedback highlights code quality, style, and improvement suggestions—without giving away solutions.

- **Assignment & Course Management:**
  - Create, edit, and publish assignments with deadlines, test cases, and language selection.
  - Organize assignments within courses; manage student enrollments.

- **User Management & Security:**
  - Role-based access for lecturers and students.
  - Secure registration, login, password reset, and email verification flows.

- **Performance & Reliability:**
  - Caching of results and feedback for speed.
  - Rate limiting to prevent abuse.
  - Robust error handling and logging.

- **API Documentation:**
  - Interactive OpenAPI/Swagger docs at `/` (localhost:8000).

---

## 🛠️ Tech Stack

- **Backend:** Django 5.1, Django REST Framework
- **Database:** PostgreSQL
- **Cache:** Redis
- **AI/LLM:** Google Gemini API
- **Code Execution:** Judge0 API
- **Auth:** JWT (SimpleJWT)

---

## ⚡ Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Osigelialex/checkmate-backend.git
cd checkmate-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
./venv/Scripts/activate  # On Windows
# or
source venv/bin/activate  # On Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Start the server**
```bash
python manage.py runserver
```

### Environment Variables

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/dbname
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_PORT=587
BASE_URL=http://localhost:8000
REDIS_LOCATION=redis://localhost:6379/1
RAPIDAPI_KEY=your-judge0-rapidapi-key
RAPIDAPI_HOST=your-judge0-rapidapi-host
GEMINI_API_KEY=your-gemini-api-key
```

---

## 📚 API Documentation

- Visit [http://localhost:8000](http://localhost:8000) for interactive Swagger/OpenAPI docs.
- All endpoints are versioned under `/api/v1/`.

---

## 🧩 Project Structure

```
├── account/              # User management (registration, login, profile)
├── assignment/           # Assignment creation, submission, grading, feedback
├── course_management/    # Course and enrollment management
├── analytics/            # Student and assignment analytics
├── checkmate/            # Django project settings and URLs
├── templates/            # Email templates
├── requirements.txt      # Python dependencies
├── manage.py             # Django management script
└── README.md             # Project documentation
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

