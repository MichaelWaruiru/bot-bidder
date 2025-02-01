from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from app.utils.mpesa import initiate_payment
from app.utils.validation import validate_phone_number
from app.models import UserModel, BidsModel
from app import mysql
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.bot import auto_bid_on_jobs
import os

dashboard_bp = Blueprint("dashboard_bp", __name__)
user_model = UserModel(mysql)
bids_model = BidsModel(mysql)

# Load subscription amount
SUBSCRIPTION_AMOUNT = os.getenv("SUBSCRIPTION_AMOUNT")

# Rate limiter for mpesa payments
limiter = Limiter(get_remote_address) # Remove app=mysql

# Setup logging for suspicious activities
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Max failed payment attempts before showing warning
MAX_FAILED_ATTEMPTS = 3

@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()  # Reads token from cookies
def dashboard():
    user_email = get_jwt_identity()  # JWT identity contains email
    user_claims = get_jwt()  #  Get full claims

    user_data = user_model.get_user_by_email(user_email)
    if not user_data:
        flash("User not found!", "danger")
        return redirect(url_for("auth_bp.login_page"))

    # Get user's bidding history
    bidding_history = bids_model.get_bidding_history(user_data[0])
    
    subscription_active = user_data[5]  # Subscription status
    access_token = session.get("access_token") if not subscription_active else None

    return render_template("dashboard.html",
                           username=user_claims["username"],  # Username from JWT claims
                           access_token=access_token, # Show only if subscription is not active
                           amount=SUBSCRIPTION_AMOUNT,
                           bidding_history=bidding_history)


@dashboard_bp.route("/get-subscription-price", methods=["GET"])
def get_subscription_price():
  """Fetch the static subscription price"""
  return jsonify({"amount": SUBSCRIPTION_AMOUNT}), 200


@dashboard_bp.route("/pay", methods=["POST"])
@jwt_required()
@limiter.limit("3 per minute")
def pay():
    """Handle payment request via MPesa STK push"""
    user_claims = get_jwt()  # Get full claims
    phone_number = user_claims.get("phone_number")  # Use claims to get phone number

    if not phone_number:
        flash("Phone number not found!", "danger")
        return redirect(url_for("dashboard_bp.dashboard"))

    # Retrieve user data using phone number
    user_data = user_model.get_user_by_phone_no(phone_number)
    if not user_data:
        flash("User not found!", "danger")
        return redirect(url_for("dashboard_bp.dashboard"))

    formatted_phone_number = phone_number.lstrip("+")
    
    # Validate phone number format
    try:
        validate_phone_number(phone_number)
    except ValueError as e:
        flash(str(e), "danger")
        return redirect(url_for("dashboard_bp.dashboard"))

    # Track failed attempts in session
    if "failed_payment_attempts" not in session:
        session["failed_payment_attempts"] = 0

    # Check if user exceeded allowed attempts
    if session["failed_payment_attempts"] >= MAX_FAILED_ATTEMPTS:
        flash("Too many failed payment attempts! Please try again later.", "danger")
        return redirect(url_for("dashboard_bp.dashboard"))

    try:
        # print(f"Initiating payment for phone: {formatted_phone_number}, amount: {SUBSCRIPTION_AMOUNT}")
        logger.info(f"Initiating payment for phone: {formatted_phone_number}, amount: {SUBSCRIPTION_AMOUNT}")


        response = initiate_payment(formatted_phone_number, int(SUBSCRIPTION_AMOUNT))

        if response.get("ResponseCode") == "0":
            flash("Payment request sent successfully. Please check your phone.", "success")
            logger.info(f"Payment request successful for phone: {formatted_phone_number}")
            
            # Reset failed attempts on success
            session["failed_payment_attempts"] = 0
        else:
            session["failed_payment_attempts"] += 1
            logger.warning(f"Payment request failed for {formatted_phone_number}")
            flash(f"Payment request failed: {response.get('errorMessage')}", "danger")
            
            #  Warn user after 3 failed attempts
            if session["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
                flash("You have exceeded the maximum number of payment attempts. Please try again later.", "warning")
                logger.warning(f"User {formatted_phone_number} exceeded max payment attempts.")
    except Exception as e:
        session["failed_payment_attempts"] += 1
        flash(f"Error processing payment: {str(e)}", "danger")
        print("Error processing payment:", e)

    return redirect(url_for("dashboard_bp.dashboard"))

@dashboard_bp.route("/bid", methods=["POST"])
@jwt_required()
def place_bid():
    """Handle automatic bid request and trigger the bot"""
    user_email = get_jwt_identity()
    user_data = user_model.get_user_by_email(user_email)
    
    if not user_data:
        flash("User not found", "danger")
        return redirect(url_for("dashboard_bp.dashboard"))
    
    # Get form data
    work_type = request.form.get("work_type")
    hours_to_submission = request.form.get("hours_to_submission")
    bid_amount = request.form.get("bid_amount")
    # Debug: Print individual values
    print("Selected Work Type:", work_type)
    print("Hours Before Submission:", hours_to_submission)
    print("Bid Amount:", bid_amount)
    
    if not work_type or not hours_to_submission or not bid_amount:
        flash("Please fill in all fields before placing a bid.", "danger")
        return redirect(url_for("dashboard_bp.dashboard"))
    
    # Store the manual bid
    bids_model.create_bid(user_data[0], work_type, hours_to_submission, bid_amount)
    
    # Check if the bot is active, then trigger automatic bidding
    bot_status = user_model.get_user_subscription_status(user_data[0]["id"])
    if bot_status == "active":
        # Trigger the bot with the work type and hours to submission
        jobs = [{"id": 1, "title": f"Job for {work_type}"}]  # Example job data, modify based on actual data
        auto_bid_on_jobs(user_data[0]["id"], jobs)
        flash("Automatic bid placed successfully!", "success")
    else:
        flash("Bot is not active. Manual bidding only.", "warning")
    
    flash("Bid placed successfully!", "success")
    return redirect(url_for("dashboard_bp.dashboard"))