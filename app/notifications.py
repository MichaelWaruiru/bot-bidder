from flask_mail import Message
from app import mail

def send_bid_notification(email, job_title):
    """Send an email notification to the user."""
    msg = Message(
        "Bid Placed Successfully!",
        sender="noreply@tst.developers69@gmail.com",
        recipients=[email]
    )
    msg.body = f"You have successfully placed a bid on '{job_title}'."
    mail.send(msg)
