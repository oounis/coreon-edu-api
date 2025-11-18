from app.background.task_queue import task_queue
from app.background.handlers.notification_tasks import (
    send_email_task,
    send_sms_task,
    send_push_task,
)

task_queue.register("send_email", send_email_task)
task_queue.register("send_sms", send_sms_task)
task_queue.register("send_push", send_push_task)
