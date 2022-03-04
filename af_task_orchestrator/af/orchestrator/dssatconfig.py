import os



os.environ['BROKER'] = 'amqp://admin:mypass@localhost:5672' #temporary for testing - later change localhost to rabbitmq
#'amqp://admin:mypass@rabbitmq:5672'

os.environ['BACKEND'] = 'rpc://'

# basic configs
broker_url = os.getenv("BROKER")
result_backend = os.getenv("BACKEND")


imports = [
    "af_task_orchestrator.af.orchestrator.processing.analyze.tasks",
    "af_task_orchestrator.af.orchestrator.processing.analyze.dssat_tasks",
    "af_task_orchestrator.af.orchestrator.processing.dssat.tasks"
]
