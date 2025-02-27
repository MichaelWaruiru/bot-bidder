# Bot-Bidder - Automated Bidding System 
## Overview
Bot bidder is an automated bidding system that allow users to select work types and set bidding preferences. The system then places bids automatically on platforms like Edusson and Writers Bay based on the user's selections. The bot is triggered automatically when the user sets their preferences and has an active subscription.

## Features
<strong>Automated Bidding</strong>: Bids on jobs based on user preferences.

<strong>User Authentication</strong>: Secure login with JWT authentication.

<strong>Subscription Management</strong>: Users must have an active subscription to enable bidding.

<strong>Dynamic Bid Amount</strong>: Users can set custom bid amounts.

<strong>Job Scraping</strong>: Uses Selenium to fetch available jobs.

<strong>Database Integration</strong>: MySQL-based backend for user data and bid tracking.

<strong>Celery Task Queue</strong>: Handles automatic job bidding in the background.

# Installation & Setup
## 1. Clone the repository 
git clone https://github.com/MichaelWaruiru/bot-bidder.git

cd bot-bidder

## 2. Install dependencies 
pip install -r requirements.txt

## 3. Configure Environment Variables
Create a .env file and add:
SECRET_KEY=your_secret_key

#JWT configurations

JWT_SECRET_KEY=

#Email configurations

#Database configurations

MYSQL_HOST=localhost
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DB=your_database


CELERY_

## 4. Run the application
<strong>Start the Flask app:</strong>

python run.py

<strong>Run redis:</strong>

memurai.exe(if downloaded from Redis server)

net start memurai(if it's the Windows service)

<strong>Verify if Redis is running:</strong>

redis-cli ping(if it's running it should return PONG)

<strong>Start the Celery worker:</strong>

celery -A app.tasks worker --loglevel=info

# Usage
1. Sign up and log in to your account.

2. Subscribe to activate bidding.

3. Set your work type preferences on the dashboard.

4. The bot automatically bids based on your selections.

5. Monitor your bidding history on the dashboard.

# Troubleshooting
(i) <strong>Celery not starting?</strong> Ensure your broker(in this case I'm using redis) is running.
 
(ii) <strong>Job not bidding?</strong>Check if your subscription is active.

(iii) <strong>Errors in Selenium?</strong> Install the correct ChromeDriver version.

# Contributions
No contributions are being accepted at this time. Thank you!

# License
This project is licensed under the MIT License.
