from flask import Blueprint, request, jsonify, render_template, current_app
from flask_jwt_extended import jwt_required
from app import mysql
from app.models import UserModel
from app.utils.mpesa import initiate_payment
import os
from datetime import datetime, timedelta
from app.utils.validation import validate_phone_number
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

subscription_bp = Blueprint('subscription', __name__)
user_model = UserModel(mysql)

# Static amount for subscription
SUBSCRIPTION_AMOUNT = int(os.getenv("SUBSCRIPTION_AMOUNT"))

# Rate limiter
limiter = Limiter(get_remote_address) # Removed app=mysql

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@subscription_bp.route("/")
def subscription_dashboard():
  return render_template("payment_dashboard.html")
      
      
@subscription_bp.route("/get-subscription-price", methods=["GET"])
def get_subscription_price():
  """Fetch the static subscription price"""
  return jsonify({"amount": SUBSCRIPTION_AMOUNT}), 200


# Rate limit: max 5 requests per minute per user/IP
@limiter.limit("5 per minute")
@subscription_bp.route("/initiate-payment", methods=["POST"])
@jwt_required()
def initiate_mpesa_payment():
  # Initiate Mpesa payment request
  data = request.get_json()
  phone_number = data.get("phoneNumber")
  
  if not phone_number:
    return jsonify({"msg": "Phone number is required"}), 400
  
  # Validate phone number format
  try:
    validate_phone_number(phone_number)
  except ValueError as e:
    return jsonify({"msg": str(e)}), 400
  
  # Logging suscpicious activities
  logger.info(f"Payment initiation request from IP: {get_remote_address()} for phone: {phone_number}")
  
  fixed_amount = SUBSCRIPTION_AMOUNT  # Enforcing static pricing
  
  # Initiate MPesa payment
  response = initiate_payment(phone_number, fixed_amount)
  if response.get("ResponseCode") == "0":
    return jsonify ({"msg": "Payment request sent. Await phone confirmation.", "checkout_request_id": response.get("CheckoutRequestID")}), 200
  else:
    logger.warning(f"Payment request failed for phone: {phone_number}, Response: {response}")
    return jsonify({"msg": "Payment request failed", "error": response}), 400
 
  
@subscription_bp.route('/mpesa-callback', methods=['POST'])
def mpesa_callback():
    """Handle MPesa callback after payment."""
    data = request.get_json()
    if data["Body"]["stkCallback"]["ResultCode"] == 0:
        phone_number = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
        
        # Find the user by phone number and activate subscription
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET subscription_active = %s, subscription_expiry = %s WHERE phone_number = %s",
                       (True, datetime.now() + timedelta(days=30), phone_number))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"msg": "Payment successful, subscription activated."}), 200
    else:
        return jsonify({"msg": "Payment failed", "error": data}), 400