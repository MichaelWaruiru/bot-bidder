from flask import Blueprint, render_template, session, flash, redirect, url_for, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from app.utils.mpesa import initiate_payment
from app.models import UserModel
from app import mysql
import os

dashboard_bp = Blueprint("dashboard_bp", __name__)
user_model = UserModel(mysql)

# Load subscription amount
SUBSCRIPTION_AMOUNT = os.getenv("SUBSCRIPTION_AMOUNT")


@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()  # ✅ Now reads token from cookies
def dashboard():
    user_email = get_jwt_identity()  # ✅ JWT identity contains email
    print("JWT Identity (Email):", user_email)  # Debugging

    user_claims = get_jwt()  # ✅ Get full claims
    print("JWT Claims:", user_claims)  # Debugging

    user_data = user_model.get_user_by_email(user_email)
    if not user_data:
        flash("User not found!", "danger")
        return redirect(url_for("auth_bp.login_page"))

    subscription_active = user_data[5]  # Subscription status
    access_token = session.get("access_token") if not subscription_active else None

    return render_template("dashboard.html",
                           username=user_claims["username"],  # ✅ Username from JWT claims
                           access_token=access_token, # Show only if subscription is not active
                           amount=SUBSCRIPTION_AMOUNT)


@dashboard_bp.route("/get-subscription-price", methods=["GET"])
def get_subscription_price():
  """Fetch the static subscription price"""
  return jsonify({"amount": SUBSCRIPTION_AMOUNT}), 200


@dashboard_bp.route("/pay", methods=["POST"])
@jwt_required()
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

    try:
        print(f"Initiating payment for phone: {formatted_phone_number}, amount: {SUBSCRIPTION_AMOUNT}")

        response = initiate_payment(formatted_phone_number, int(SUBSCRIPTION_AMOUNT))

        if response.get("ResponseCode") == "0":
            flash("Payment request sent successfully. Please check your phone.", "success")
        else:
            flash(f"Payment request failed: {response.get('errorMessage')}", "danger")
    except Exception as e:
        flash(f"Error processing payment: {str(e)}", "danger")
        print("Error processing payment:", e)

    return redirect(url_for("dashboard_bp.dashboard"))
