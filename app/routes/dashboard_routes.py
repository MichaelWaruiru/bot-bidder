from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils.mpesa import initiate_payment
from app.models import UserModel
from app import mysql
import os

dashboard_bp = Blueprint("dashboard_bp", __name__)
user_model = UserModel(mysql)

# Load subscription amount
SUBSCRIPTION_AMOUNT = os.getenv("SUBSCRIPTION_AMOUNT")


@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
  if not session:
    flash("Session expired. Please log in again", "danger")
    return redirect(url_for("dashboard_bp.dashboard"))
  
  user = get_jwt_identity() # Get logged-in user details from JWT
  user_data = user_model.get_user_by_email(user[3])
  
  if not user_data:
    flash("User not found!", "danger")
    return redirect(url_for("auth_bp.login_page"))
  
  subscription_active = user_data[5] # Subscription_active column True/False
  access_token = session.get("access_token") if not subscription_active else None
  
  return render_template("dashboard.html", 
                         username=user[2], 
                         access_token=access_token, # Show only if subscription is not active
                         amount=SUBSCRIPTION_AMOUNT
                        )

@dashboard_bp.route("/get-subscription-price", methods=["GET"])
def get_subscription_price():
  """Fetch the static subscription price"""
  return jsonify({"amount": SUBSCRIPTION_AMOUNT}), 200

# @dashboard_bp.route("/pay", methods=["POST"])
# @jwt_required()
# def pay():
#   """Handle payment request via MPesa STK push"""
#   user = get_jwt_identity()
#   user_data = user_model.get_user_by_email(user[3])
  
#   if not user_data:
#     flash("User not found!", "danger")
#     return redirect(url_for("dashboard_bp.dashboard"))
  
#   phone_number = user_data[3] # Retrieve number from database
  
#   # Format the phone number
#   formatted_no = phone_number.lstrip("+")
#   print(formatted_no)
#   if not phone_number:
#     flash("Phone number not found!", "danger")
#     return redirect(url_for("dashboard_bp.dashboard"))
  
#   try:
#     print(f"Initiating payment for phone: {formatted_no}, amount: {SUBSCRIPTION_AMOUNT}")
    
#     response = initiate_payment(phone_number, int(SUBSCRIPTION_AMOUNT))
#     print("MPesa Response:", response)
    
#     if response.get("ResponseCode") == "0":
#       flash("Payment request sent successfully. Please check your phone.", "success")
#     else:
#       flash("Payment request failed. Try again later.", "danger")
#   except Exception as e:
#     flash(f"Error proccessing payment: {str(e)}", "danger")
    
#   return redirect(url_for("dashboard_bp.dashboard"))
@dashboard_bp.route("/pay", methods=["POST"])
@jwt_required()
def pay():
    print("Pay route called")  # Add this to confirm route execution

    user = get_jwt_identity()
    print(f"JWT Identity: {user}")  # Log JWT identity

    user_data = user_model.get_user_by_email(user[3])  # Access user phone number
    print(f"User Data: {user_data}")  # Log user data

    if not user_data:
        flash("User not found!", "danger")
        return redirect(url_for("dashboard_bp.dashboard"))

    phone_number = user_data[3]  # Retrieve phone number from the database
    print(f"Phone Number: {phone_number}")  # Log phone number

    if not phone_number:
        flash("Phone number not found!", "danger")
        return redirect(url_for("dashboard_bp.dashboard"))

    # Ensure phone number is correctly formatted
    formatted_phone_number = phone_number.lstrip("+")
    print(f"Formatted Phone Number: {formatted_phone_number}")

    try:
        print(f"Initiating payment for phone: {formatted_phone_number}, amount: {SUBSCRIPTION_AMOUNT}")

        response = initiate_payment(formatted_phone_number, int(SUBSCRIPTION_AMOUNT))
        print("MPesa Response:", response)

        if response.get("ResponseCode") == "0":
            flash("Payment request sent successfully. Please check your phone.", "success")
        else:
            flash(f"Payment request failed: {response.get('errorMessage')}", "danger")
    except Exception as e:
        flash(f"Error processing payment: {str(e)}", "danger")
        print("Error processing payment:", e)

    return redirect(url_for("dashboard_bp.dashboard"))
