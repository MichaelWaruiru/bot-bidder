# bot-bidder - Automated Bidding System 
## Overview
Bot bidder is an automated bidding system that allow users to select work types and set bidding preferences. The system then places bids automatically on platforms like Edusson and Writers Bay based on the user's selections. The bot is triggered automatically when the user sets their preferences and has an active subscription.

# Features

Automated Bidding: Bids on jobs based on user preferences.

User Authentication: Secure login with JWT authentication.

Subscription Management: Users must have an active subscription to enable bidding.

Dynamic Bid Amount: Users can set custom bid amounts.

Job Scraping: Uses Selenium to fetch available jobs.

Database Integration: MySQL-based backend for user data and bid tracking.

Celery Task Queue: Handles automatic job bidding in the background.

## Installation & Setup
# 1. Clone the repository 
git clone https://github.com/MichaelWaruiru/bot-bidder.git
cd bot-bidder
