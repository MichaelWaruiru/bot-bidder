from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from app.models import UserModel
from app.notifications import send_bid_notification
from app.scraper import intialize_driver

def initialize_driver():
    service = Service("chrome.exe")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.ChromeOptions(service=service, options=options)
    return driver

def auto_bid_on_jobs(user_id, jobs, bid_amount):
    """Automate the bidding process for matched jobs."""
    user_data = UserModel.get_user_by_id(user_id)
    login_url = "https://edusson.com/login"  # Example site
    
    driver = intialize_driver()

    # Login to the platform
    driver.get(login_url)
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )

    driver.find_element(By.NAME, "email").send_keys(user_data["email"])
    driver.find_element(By.NAME, "password").send_keys(user_data["password"])
    driver.find_element(By.ID, "login-btn").click()

    for job in jobs:
        bid_url = f"https://edusson.com/job/{job['id']}/bid"
        driver.get(bid_url)
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "bid_amount"))
        )

        # Use the dynamic bid amount here
        driver.find_element(By.NAME, "bid_amount").send_keys(bid_amount)
        driver.find_element(By.NAME, "cover_letter").send_keys("I am the best fit for this job.")
        driver.find_element(By.ID, "bid-btn").click()
        
        # Wait to ensure the bid is submitted
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )

        # Send notification
        send_bid_notification(user_data["email"], job["title"])

    driver.quit()
