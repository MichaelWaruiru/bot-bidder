# Bot-Bidder - Automated Bidding System 
## Overview
Bot bidder is an automated bidding system that allow users to select work types and set bidding preferences. The system then places bids automatically on platforms like Edusson and Writers Bay based on the user's selections. The bot is triggered automatically when the user sets their preferences and has an active subscription.

## Features
Automated Bidding: Bids on jobs based on user preferences.

User Authentication: Secure login with JWT authentication.

Subscription Management: Users must have an active subscription to enable bidding.

Dynamic Bid Amount: Users can set custom bid amounts.

Job Scraping: Uses Selenium to fetch available jobs.

Database Integration: MySQL-based backend for user data and bid tracking.

Celery Task Queue: Handles automatic job bidding in the background.

# Installation & Setup
## 1. Clone the repository 
git clone https://github.com/MichaelWaruiru/bot-bidder.git

cd bot-bidder

## 2. Install dependencies 
pip install -r requirements.txt

## 3. Configure Environment Variables
Create a .env file and add:
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_DB=your_database
CELERY_BROKER_URL= "redis://localhost:6379/0"
CELERY_RESULT_BACKEND=db+mysql://your_user:your_password@localhost/your_database

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
Feel free to contribute by submitting pull requests or reporting issues.

# License
This project is licensed under the MIT License.
