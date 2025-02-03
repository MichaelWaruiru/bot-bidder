from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from app.models import BiddingPreferenceModel
from app import mysql

def intialize_driver():
  """Intialize the WebDriver with necessary options."""
  service = Service("chromedriver.exe")
  options = webdriver.ChromeOptions() # Path to ChromeDriver
  options.add_argument("---headless") # Run in headless mode
  driver = webdriver.Chrome(service=service, options=options)
  return driver

def scrape_jobs():
  job_sites = {
    "Edusson": "https://edusson.com/jobs",
    "Writers Bay": "https://writersbay.com/jobs"
  }
  
  job_listings = []
  driver = intialize_driver()
  
  for site, url in job_sites.items():
    driver.get(url)
    
    # Use WebDriverWait to ensure page is fully loaded
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CLASS_NAME, "job-card"))
    )
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    jobs = soup.find_all("div", class_="job-card")
    
    for job in jobs:
      title = job.find("h3").text.strip()
      deadline = job.find("span", class_="deadline").text.strip()
      work_type = job.find("span", class_="category").text.strip()
      
      job_listings.append({
        "site": site,
        "title": title,
        "deadline": int(deadline),
        "work_type": work_type
      })
      
  driver.quit()
  return job_listings


def filter_jobs_for_user(user_id, jobs):
  # Filter jobs based on user preferences
  user_prefs = BiddingPreferenceModel(mysql).get_user_preferences(user_id)
  preferred_work_types = user_prefs["work_types"]
  max_hours_to_submission = user_prefs["hours_to_subsmission"]
  
  return [
    job for job in jobs if job["work_type"] in preferred_work_types and job["deadline"] <= max_hours_to_submission
  ]