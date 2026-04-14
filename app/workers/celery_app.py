from celery import Celery

celery = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery.conf.task_routes = {
    "app.workers.tasks.process_resume": {"queue": "default"}
}