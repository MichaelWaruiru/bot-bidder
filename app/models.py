class UserModel:
  def __init__(self, mysql):
    self.mysql = mysql
    
  def create_user(self, username, email, phone_number, password_hash):
    cursor = self.mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, email, phone_number, password_hash) VALUES (%s, %s, %s, %s)", (username, email, phone_number, password_hash))
    self.mysql.connection.commit()
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
        cursor.execute("SELECT bot_active FROM users WHERE id = %s", (user_id,))
        status = cursor.fetchone()
        cursor.close()
        return status[0] if status else 'inactive'
  
  def update_bot_status(self, user_id, status):
    cursor = self.mysql.connection.cursor()
    cursor.execute("UPDATE users SET bot_active = %s WHERE id = %s", status, user_id)
    self.mysql.connection.cursor()
    cursor.close()
    
    
def log_payment_attempt(self, user_id, phone_number, amount, status, reason=None):
  """Logs each payment attempt into the database"""
  cursor = self.mysql.connection.cursor()
  cursor.execute("INSERT INTO payment_attempts (user_id, phone_number, amount, status, reason)", user_id, phone_number, amount, status, reason)
  self.mysql.connection.commit()
  cursor.close()
  

def get_payment_attempts(self, user_id):
  """Fetches a user's payment attempts."""
  cursor = self.mysql.connection.cursor()
  cursor.execute("""SELECT phone_number, amount, status, reason, attempt_time 
                    FROM payment_attempts WHERE user_id = %s ORDER BY attempt_time DESC""", 
                    (user_id,)
                )
  attempts = cursor.fetchall()
  cursor.close()
  return attempts


def count_failed_attempts(self, user_id):
    """Counts the number of failed attempts for a user in the last hour"""
    cursor = self.mysql.connection.cursor()
    cursor.execute("""SELECT COUNT(*) FROM payment_attempts 
                      WHERE user_id = %s AND status = 'failed' AND created_at >= NOW() - INTERVAL 1 HOUR""", 
                      (user_id,)
                  )
    failed_count = cursor.fetchone()[0]
    cursor.close()
    return failed_count