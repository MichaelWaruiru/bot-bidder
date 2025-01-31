from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from app.models import BiddingPreferenceModel
from app import mysql

def scrape_jobs():
  # Scrapes job listings from multiple freelance platforms
  service = Service("chromedriver.exe") # Path to ChromeDriver
  options = webdriver.ChromeOptions()
  options.add_argument("--headless") # Run in Chrome headless mode
  driver = webdriver.Chrome(service=service, options=options)
  
  job_sites = {
    "Edusson": "https://edusson.com/jobs",
    "Writers Bay": "https://writersbay.com/jobs"
  }
  
  job_listings = []
  
  for site, url in job_sites.items():
    driver.get(url)
    time.sleep(3) # Wait for the page to load
    
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