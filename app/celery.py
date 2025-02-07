# from celery import Celery
# from app import create_app
# from app.config import Config

# app = create_app()
# app.config.from_object(Config)

# def make_celery(app):
#     """Initialize Celery with Flask app context."""
#     celery = Celery(
#         app.import_name,
#         backend=app.config["CELERY_RESULT_BACKEND"],
#         broker=app.config["CELERY_BROKER_URL"]
#     )
#     celery.conf.update(app.config)
    
    
#     class ContextTask(celery.Task):
#         """Ensure Celery tasks run with Flask app context."""
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
            
#     celery.Task = ContextTask
#     return celery

# Celery = make_celery(app)
from celery import Celery
from app import create_app
from app.config import Config

app = create_app()
app.config.from_object(Config)

celery = Celery(
    app.import_name,
    backend=app.config["CELERY_RESULT_BACKEND"],
    broker=app.config["CELERY_BROKER_URL"]
)
celery.conf.update(app.config)

class ContextTask(celery.Task):
    """Ensure Celery tasks run with Flask app context."""
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
