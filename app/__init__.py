from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from flask_cors import CORS

load_dotenv()

mysql = MySQL()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app():
  app = Flask(__name__)
  
  # Load configurations
  app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
  app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
  app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))
  app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
  app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
  app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
  app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
  
  mysql.init_app(app)
  bcrypt.init_app(app)
  jwt.init_app(app)
  
  # Enable CORS for a specific origin
  CORS(app, resources={r"/api/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization"], supports_credentials=True)  # Allow only from 127.0.0.1
  
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
  
  # Register routes here to avoid circular imports
  from app.routes.auth_routes import auth_bp
  from app.routes.bot_routes import bot_bp
  from app.routes.dashboard_routes import dashboard_bp
  
  app.register_blueprint(auth_bp, url_prefix="/api/auth")
  app.register_blueprint(bot_bp, url_prefix="/api/bot")
  app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
  
  return app