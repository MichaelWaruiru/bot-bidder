from celery import Celery

celery = Celery()

def make_celery(app):
    """Initialize Celery with Flask app context."""
    celery.config_from_object(app.config)

    class ContextTask(celery.Task):
        """Ensure Celery tasks run with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def init_celery(app):
    """Initialize the global Celery instance with Flask app."""
    make_celery(app)  # Assign configuration to global `celery`