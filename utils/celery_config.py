import os
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=os.getenv('CELERY_BROKER_URL'),
        backend=os.getenv('CELERY_RESULT_BACKEND'),
        include=["services.instagram_service"]
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
