import os

from celery import Celery

CELERY_APP = None


os.environ['BROKER'] = 'amqp://admin:mypass@localhost:5672' #temporary for testing - later change localhost to rabbitmq


def get_celery_app():  # pragma: no cover
    BROKER = os.getenv("BROKER")

    app = Celery("af-tasks", broker=BROKER)
    app.conf.update({"task_serializer": "pickle"})
    return app


def send_task(process_name, args, queue="default", routing_key="default"):  # pragma: no cover
    global CELERY_APP
    if not CELERY_APP:
        CELERY_APP = get_celery_app()

    CELERY_APP.send_task(process_name, args=args, queue=queue, routing_key=routing_key)
