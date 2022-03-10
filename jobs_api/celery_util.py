import os

from celery import Celery

CELERY_APP = None


os.environ['BROKER'] = 'amqp://admin:mypass@localhost:5672' #?# temporary for testing - later change localhost to rabbitmq

os.environ['BACKEND'] = 'rpc://' #?#


def get_celery_app():  # pragma: no cover
    BROKER = os.getenv("BROKER")
    BACKEND = os.getenv("BACKEND")

    app = Celery("af-tasks", broker=BROKER, backend=BACKEND, accept_content = ['json', 'pickle'])
    app.conf.update({"task_serializer": "pickle"})
    return app


def send_task(process_name, args, queue="default", routing_key="default"):  # pragma: no cover
    global CELERY_APP
    if not CELERY_APP:
        CELERY_APP = get_celery_app()

    CELERY_APP.send_task(process_name, args=args, queue=queue, routing_key=routing_key)


def send_task_get(process_name, args, queue="default", routing_key="default"):  # pragma: no cover
    global CELERY_APP
    if not CELERY_APP:
        CELERY_APP = get_celery_app()

    return CELERY_APP.send_task(process_name, args=args, queue=queue, routing_key=routing_key).get()
