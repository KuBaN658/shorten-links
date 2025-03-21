from celery import Celery

app = Celery(
    "tasks", 
    broker="redis://localhost:6379/1", 
    backend="redis://localhost:6379/1"
)

app.conf.timezone = "UTC"
