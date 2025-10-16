# **Car Dealer System (CDS)**

**Car Dealer System** — is a comprehensive backend system for managing car dealerships, buyers and suppliers. The system automates the processes of sales, purchases, promotions and car purchase offers using Django, Celery, PostgreSQL и Redis.

![Django](https://img.shields.io/badge/Django-5.2.7-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)
![Redis](https://img.shields.io/badge/Redis-8-red)
![Docker](https://img.shields.io/badge/Docker-✓-blue)
![Celery](https://img.shields.io/badge/Celery-Python-orange)

⚙️ Tech Stack
- **Backend:** Django + Django REST Framework  
- **Database:** PostgreSQL  
- **Caching:** Redis  
- **Asynchrony:** Celery + Celery Beat, Redis
- **Containerization:** Docker, Docker Compose  
- **Authorization:** JWT (SimpleJWT)  
- **Documentation:** Swagger (drf-yasg)  
- **Filters:** django-filters  
- **Управление зависимостями:** Pipenv
- **Development Tools**:
    1. Django Debug Toolbar
    2. flake8, black, pylint, mypy, isort
    3. Pytest, Unittest, Faker

## 🚀 Quick Start

### 📁 Clone the Repository

```bash
git clone https://github.com/TekkenBro7/car_dealer_system.git
cd car_dealer_system
```

### ⚙️ Setup `.env` File

Create a `.env` file in your root based on `.env.example`

### Installing dependencies via Pipenv

Install Pipenv if not already installed:
```bash
pip install pipenv
```

Install project dependencies
```bash
pipenv install
```

You can activate the virtual environment using the command `pipenv shell` or write before each command `pipenv run`

Before making any commits, run the following command to set up the pre-commit hooks:
```bash
pre-commit install
```

To test pre-commit hooks without a commit, use
```bash
pipenv run pre-commit run --all-files
```

### 🐳 Running with Docker

To start the app using Docker:
```bash
docker-compose up --build
```
And make sure that the `env` file states `POSTGRES_HOST=db` and `REDIS_HOST=redis`

- Django will run on `http://localhost:8000`
- PostgreSQL is available at port `5432`
- Redis runs on port `6379`

### Run Locally

1. Ensure PostgreSQL and Redis are installed and running
2. Create a PostgreSQL database and grant privileges usern `.env` variables like
```bash
CREATE DATABASE car_dealer;
CREATE USER car_dealer_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE car_dealer TO car_dealer_user;
```
3. Apply migrations
```bash
pipenv run python src/manage.py migrate
```
4. Ensure `.env` specifies `POSTGRES_HOST=localhost` and `REDIS_HOST=localhost`
5. Start the development server
```bash
pipenv run python src/manage.py runserver
```
