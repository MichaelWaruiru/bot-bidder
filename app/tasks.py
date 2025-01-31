from app import create_app
from app.scraper import scrape_jobs, filter_jobs_for_user
from app.models import UserModel
from app.bot import auto_bid_on_jobs
from app.celery import make_celery
from app import mysql

# Initialize Flask App & Celery
app = create_app()
celery = make_celery(app)

@celery.task
def automated_bidding():
    """Scrapes jobs, filters them, and bids automatically."""
    with app.app_context():
        jobs = scrape_jobs()
        users = UserModel(mysql).get_all_users()

        for user in users:
            matched_jobs = filter_jobs_for_user(user["id"], jobs)
            if matched_jobs:
                auto_bid_on_jobs(user["id"], matched_jobs)
