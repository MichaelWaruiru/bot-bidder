from celery import Celery

def make_celery(app):
    """Initialize Celery with Flask app context."""
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
    return celery
