from app import create_app
from app.scraper import scrape_jobs, filter_jobs_for_user
from app.models import UserModel, BiddingPreferenceModel
from app.bot import auto_bid_on_jobs
from app.celery import make_celery
from app import mysql

# Initialize Flask App & Celery
app = create_app()
celery = make_celery(app)

@celery.task(bind=True)
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
                    preferences = BiddingPreferenceModel(mysql).get_user_preferences(user["id"])
                    work_types = preferences["work_types"]
                    hours_to_submission = preferences["hours_to_submission"]
                    bid_amount = preferences["bid_amount"]
                    
                    # Match only jobs relevant to user's work types
                    matched_jobs = filter_jobs_for_user(user["id"], jobs, work_types, hours_to_submission)
                    if matched_jobs:
                        auto_bid_on_jobs(user["id"], matched_jobs, bid_amount)
                        
        except Exception as e:
            self.retry(exc=e, countdown=60) # Retry after 60 seconds if failed
