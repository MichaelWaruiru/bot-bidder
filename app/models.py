class UserModel:
  def __init__(self, mysql):
    self.mysql = mysql
    
  def create_user(self, username, email, phone_number, password_hash):
    # Wrap user creation in a transaction
    cursor = self.mysql.connection.cursor()
    try:
      cursor.execute("START TRANSACTION")
      cursor.execute("INSERT INTO users (username, email, phone_number, password_hash) VALUES (%s, %s, %s, %s)", 
                      (username, email, phone_number, password_hash))
      cursor.execute("COMMIT")
    except Exception as e:
      cursor.execute("ROLLBACK")
      raise e
    finally:
      cursor.close()
      
  def get_user_by_email(self, email):
    cursor = self.mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user
  
  def get_user_by_phone_no(self, phone_number):
    cursor = self.mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE phone_number = %s", (phone_number,))
    user = cursor.fetchone()
    cursor.close()
    return user
  
  def get_user_by_username(self, username):
    cursor = self.mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user
  
  def get_user_subscription_status(self, user_id):
    cursor = self.mysql.connection.cursor()
    cursor.execute("SELECT subscription_active, subscription_expiry FROM users WHERE id = %s", (user_id,))
    status = cursor.fetchone()
    cursor.close()
    return status[0] if status else 'inactive'
  
  def update_subscription_status(self, user_id, subscription_active, subscription_expiry):
    cursor = self.mysql.connection.cursor()
    cursor.execute("UPDATE users SET subscription_active = %s, subscription_expiry = %s WHERE id = %s", 
                    (subscription_active, subscription_expiry, user_id))
    self.mysql.connection.commit()
    cursor.close()
  
  def update_bot_status(self, user_id, status):
    cursor = self.mysql.connection.cursor()
    cursor.execute("UPDATE users SET bot_active = %s WHERE id = %s", (status, user_id))
    self.mysql.connection.commit()
    cursor.close()
    
    
  def update_last_login_ip(self, user_id, ip_address):
      cursor = self.mysql.connection.cursor()
      cursor.execute("UPDATE users SET last_login_ip = %s WHERE id = %s", (ip_address, user_id))
      self.mysql.connection.commit()
      cursor.close()


  def log_payment_attempt(self, user_id, phone_number, amount, status, reason=None):
    """Logs each payment attempt into the database"""
    cursor = self.mysql.connection.cursor()
    cursor.execute("INSERT INTO payment_attempts (user_id, phone_number, amount, status, reason) VALUES (%s, %s, %s, %s, %s)", 
                    (user_id, phone_number, amount, status, reason))
    self.mysql.connection.commit()
    cursor.close()
    

  def get_payment_attempts(self, user_id):
    """Fetches a user's payment attempts."""
    cursor = self.mysql.connection.cursor()
    cursor.execute("""SELECT phone_number, amount, status, reason, attempt_time 
                      FROM payment_attempts WHERE user_id = %s ORDER BY attempt_time DESC""", 
                    (user_id,))
    attempts = cursor.fetchall()
    cursor.close()
    return attempts


  def count_failed_attempts(self, user_id):
    """Counts the number of failed attempts for a user in the last hour"""
    cursor = self.mysql.connection.cursor()
    cursor.execute("""SELECT COUNT(*) FROM payment_attempts 
                      WHERE user_id = %s AND status = 'failed' AND created_at >= NOW() - INTERVAL 1 HOUR""", 
                    (user_id,))
    failed_count = cursor.fetchone()[0]
    cursor.close()
    return failed_count


class BiddingPreferenceModel:
  # Handles user preferences for automated bidding
  def __init__(self, mysql):
    self.mysql = mysql
    

  def set_user_preferences(self, user_id, work_types, hours_to_submission, bid_amount):
    # Save or update user bidding preferences
    cursor = self.mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO bidding_preferences (user_id, work_types, hours_to_submission, bid_amount) 
        VALUES (%s, %s, %s, %s) 
        ON DUPLICATE KEY UPDATE work_types = VALUES(work_types), 
                                hours_to_submission = VALUES(hours_to_submission), 
                                bid_amount = VALUES(bid_amount)
    """, (user_id, work_types, hours_to_submission, bid_amount))
    self.mysql.connection.commit()
    cursor.close()
    
    
  def get_user_preferences(self, user_id):
    # Retrieves user bidding preferences
    cursor = self.mysql.connection.cursor()
    cursor.execute("SELECT work_types, hours_to_submission FROM bidding_preferences WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    
    if row:
        return {"work_types": row[0].split(",") if row[0] else [], "hours_to_submission": row[1] if row[1] else 0}
    return {"work_types": [], "hours_to_submission": 0}


class BidsModel:
  """Handles automatic bids from users."""
  def __init__(self, mysql):
      self.mysql = mysql

  def create_bid(self, user_id, work_type, hours_to_submission):
    cursor = self.mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO bids (user_id, work_type, hours_to_submission, bid_time, status)
        VALUES (%s, %s, %s, NOW(), 'PENDING')
    """, (user_id, work_type, hours_to_submission))
    self.mysql.connection.commit()
    cursor.close()

  def get_bidding_history(self, user_id):
    cursor = self.mysql.connection.cursor()
    cursor.execute("""
        SELECT work_type, hours_to_submission, bid_time, status
        FROM bids WHERE user_id = %s ORDER BY bid_time DESC
    """, (user_id,))
    history = cursor.fetchall()
    cursor.close()
    return history
