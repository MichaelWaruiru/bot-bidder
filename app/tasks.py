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
def automated_bidding(self):
    """Scrapes jobs, filters them, and bids automatically for subscribed users."""
    with app.app_context():
        try:
            jobs = scrape_jobs()
            user_model = UserModel(mysql)
            users = user_model.get_all_users()

            for user in users:
                subscription_data = UserModel(mysql).get_user_subscription_status(user["id"])
                
                if subscription_data["subscription_active"]:
                    matched_jobs = filter_jobs_for_user(user["id"], jobs)
                    if matched_jobs:
                        auto_bid_on_jobs(user["id"], matched_jobs)
                        
        except Exception as e:
            self.retry(exc=e, countdown=60) # Retry after 60 seconds if failed
