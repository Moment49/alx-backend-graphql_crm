Document setup:

# CRM Celery Setup

## Installation
```bash
pip install -r requirements.txt

Redis

Make sure Redis is running:

sudo apt-get install redis-server
sudo service redis-server start

Migrations
python manage.py migrate

Running Celery

Start Celery worker:

celery -A crm worker -l info


Start Celery Beat scheduler:

celery -A crm beat -l info

Logs

Weekly reports will be written to:

/tmp/crm_report_log.txt


Format:

YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue


---

✅ This setup makes sure your **Celery worker runs weekly reports every Monday at 6:00 AM**, fetches GraphQL data, and logs it properly.  

Do you also want me to include a **fallback Django management command** for generating the report manually (in case Celery isn’t running)?
