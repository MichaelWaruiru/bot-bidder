from flask import Blueprint, request, session, render_template, flash, redirect, url_for
from app import mysql, bcrypt
from flask_jwt_extended import create_access_token
from app.models import UserModel
from app.utils.validation import validate_phone_number

auth_bp = Blueprint("auth_bp", __name__)
user_model = UserModel(mysql)


# Route to render the registration form
@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

# Route to handle registration form submission
@auth_bp.route("/register", methods=["POST"])
def register():
    # data = request.get_json()
    username = request.form.get("username")
    email = request.form.get("email").strip().lower() # Stores email in lower case in db
    phone_number = request.form.get("phone_number")
    formatted_phone = format_phone_number(phone_number)
    password = bcrypt.generate_password_hash(request.form.get("password")).decode("utf-8")
    
    if not password:
        flash("Password cannot be empty", "danger")
        return redirect(url_for("auth_bp.register_page"))

    existing_user = user_model.get_user_by_email(email)
    if existing_user:
        flash("User already exists", "danger")
        return redirect(url_for("auth_bp.register_page"))

    user_model.create_user(username, email, formatted_phone, password)
    flash(f"{username} has been registered successfully!", "success")
    return redirect(url_for("auth_bp.login_page"))

def format_phone_number(phone):
    """Ensure phone number is in +254 format"""
    phone = phone.strip().replace(" ", "")  # Remove spaces
    if phone.startswith("0"):
        return "+254" + phone[1:]  # Convert 07xxxxxxxx to +2547xxxxxxxx
    elif phone.startswith("1"):
        return "+254" + phone       # Convert 1xxxxxxxx to +2541xxxxxxxx
    elif phone.startswith("254"):
        return "+254" + phone[3:]   # Convert 254xxxxxxxxx to +2547xxxxxxxx
    elif not phone.startswith("+254"):
        return "+254" + phone       # Add prefix if missing
    return validate_phone_number(phone)

# Route to render the login form
@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

# Route to handle login form submission
@auth_bp.route("/login", methods=["POST"])
def login():
    # data = request.get_json()
    email = request.form.get("email")
    password = request.form.get("password")

    user = user_model.get_user_by_email(email)
    if user and bcrypt.check_password_hash(user[4], password):
        access_token = create_access_token(identity={"email": email, "id": user[0], "phone_number": user[3]})
        session["access_token"] = access_token
        flash("Login successful!", "success")
        return render_template("dashboard.html", access_token=access_token)
    else:
        flash("Invalid credentials", "danger")
        return redirect(url_for("auth_bp.login_page"))
