from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_mail import Mail
from app.config import Config

mysql = MySQL()
bcrypt = Bcrypt()
jwt = JWTManager()
mail = Mail()


def create_app():
  app = Flask(__name__)
  
  # Load configurations
  app.config.from_object(Config)

  mysql.init_app(app)
  bcrypt.init_app(app)
  jwt.init_app(app)
  mail.init_app(app)

  # Fix CORS Issues
  CORS(app, supports_credentials=True)  

  # Debugging MySQL connection
  try:
      with app.app_context():
          cur = mysql.connection.cursor()
          cur.execute("SELECT DATABASE();")
          db_name = cur.fetchone()
          print(f"Connected to database: {db_name}")
          cur.close()
  except Exception as e:
      print(f"Database connection failed: {e}")

  # Register routes here
  from app.routes.auth_routes import auth_bp
  from app.routes.dashboard_routes import dashboard_bp

  app.register_blueprint(auth_bp, url_prefix="/api/auth")
  app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

  return app