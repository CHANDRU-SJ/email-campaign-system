## 📧 Email Campaign Management System (DRF + Celery + PostgreSQL)

A production-ready Django REST Framework application for creating, scheduling, and sending bulk email campaigns asynchronously using Celery. Includes a local SMTP server for testing.

***

### 🧱 Tech Stack

- Backend: Django REST Framework
- Database: PostgreSQL
- Task Queue: Celery
- Broker: Redis
- Email Server: Local SMTPD
- Scheduler: Celery Beat

***

### ⚙️ Prerequisites

Make sure the following tools are installed on your system:


| Tool | Version | Check Command |
| :-- | :-- | :-- |
| Python | ≥ 3.10 | `python --version` |
| pipenv | Latest | `pip install pipenv` |
| PostgreSQL | ≥ 14 | `psql --version` |
| Redis | ≥ 6 | `redis-server --version` |


***

### 🚀 Setup Instructions

#### 1️⃣ Clone the Repository

```
git clone https://github.com/CHANDRU-SJ/email-campaign-system.git
cd email_campaign_system
```


#### 2️⃣ Create and Activate Virtual Environment

```
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows
```


#### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```


#### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```
touch .env
```

Add the following:

```
# Django
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=*

# Database
DB_NAME=db_name
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=5432

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Email
EMAIL_HOST=localhost
EMAIL_PORT=1025
EMAIL_USE_TLS=False

FROM_EMAIL=no-reply@company.com
ADMIN_EMAIL=admin@company.com
```


***

### 🛠 Database Setup

```
python manage.py makemigrations
python manage.py migrate
```


***

### ⚙️ Run Required Services

#### Start Redis Server

```
redis-server
```

if you don't have docker setup use below docker-compose.yml setup
```
version: "3.8"

services:
  redis:
    image: redis:7-alpine
    container_name: redis_server
    ports:
      - "6379:6379"
    restart: always
```
##### Start Redis
`docker-compose up -d redis`


#### Start Local SMTP Server

Logs all outgoing emails to the console:

```
python -m smtpd -c DebuggingServer -n localhost:1025
```


#### Start Celery Worker

```
celery -A email_campaign_system worker --loglevel=info --pool=solo
```


#### Start Celery Beat (Scheduler)

```
celery -A email_campaign_system beat --loglevel=info
```


#### Start Django Server

```
python manage.py runserver
```


***

### 🧪 Verify the Setup

- Open the app: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Access Swagger docs (if enabled): [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- Create and schedule a new campaign: [http://127.0.0.1:8000/campaigns/create/form/](http://127.0.0.1:8000/campaigns/create/form/)
- Wait for Celery Beat to trigger the task
- Check the SMTPD terminal to view email logs

***

### 🧹 Stop Services

Press `CTRL + C` in each terminal window (Django, Celery workers, Beat, Redis, SMTPD).

***

### ✅ Summary of Running Commands

```
# Terminal 1
pipenv shell
python manage.py runserver

# Terminal 2
redis-server

# Terminal 3
celery -A email_campaign_system worker --loglevel=info --pool=solo

# Terminal 4
celery -A email_campaign_system beat --loglevel=info

# Terminal 5
python -m smtpd -c DebuggingServer -n localhost:1025
```