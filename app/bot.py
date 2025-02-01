from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from app.models import UserModel
from app.notifications import send_bid_notification

def auto_bid_on_jobs(user_id, jobs, bid_amount):
    """Automate the bidding process for matched jobs."""
    user_data = UserModel.get_user_by_id(user_id)
    login_url = "https://edusson.com/login"  # Example site

    service = Service("chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)

    # Login to the platform
    driver.get(login_url)
    time.sleep(2)

    driver.find_element(By.NAME, "email").send_keys(user_data["email"])
    driver.find_element(By.NAME, "password").send_keys(user_data["password"])
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(3)

    for job in jobs:
        bid_url = f"https://edusson.com/job/{job['id']}/bid"
        driver.get(bid_url)
        time.sleep(2)

        # Use the dynamic bid amount here
        driver.find_element(By.NAME, "bid_amount").send_keys(bid_amount)
        driver.find_element(By.NAME, "cover_letter").send_keys("I am the best fit for this job.")
        driver.find_element(By.ID, "bid-btn").click()
        time.sleep(2)

        # Send notification
        send_bid_notification(user_data["email"], job["title"])

    driver.quit()
