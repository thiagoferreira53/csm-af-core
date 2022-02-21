# import os
import jsonpickle.ext.pandas as jsonpickle_pandas
from celery import Celery
from celery.utils.log import get_task_logger
from kombu import Exchange, Queue

jsonpickle_pandas.register_handlers()
# register('json', jsonpickle.dumps, jsonpickle.loads, content_type='application/json')


LOGGER = get_task_logger(__name__)

# INSTALLED_TASKS = ["af-core.orchestrator.processing.analyze", "af-core.orchestrator.processing.asreml"]

default_queue_name = "default"
default_exchange_name = "default"
default_routing_key = "default"

dssat_queue_name = "DSSAT"
asreml_queue_name = "ASREML"
asreml_routing_key = "ASREML"
dssat_routing_key = "DSSAT"

app = Celery()

app.conf.update({"accept_content": ["pickle"], "task_serializer": "pickle", "result_serializer": "pickle"})

default_exchange = Exchange(default_exchange_name, type="direct")

default_queue = Queue(default_queue_name, default_exchange, routing_key=default_routing_key)
asreml_queue = Queue(asreml_queue_name, default_exchange, routing_key=asreml_routing_key)
dssat_queue = Queue(dssat_queue_name, default_exchange, routing_key=dssat_routing_key)


app.conf.task_queues = (default_queue, asreml_queue, dssat_queue)
app.conf.task_default_queue = default_queue_name
app.conf.task_default_exchange_name = default_exchange_name
app.conf.task_default_routing_key = default_routing_key
