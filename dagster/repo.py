import time

from dagster import FilesystemIOManager, job, op, repository, schedule
from resource.telegram_notification_resources import telegram_notification


@op(required_resource_keys={"telegram_notification"})
def hello(context):
    context.resources.telegram_notification.send_message('test info message', 'info')
    context.resources.telegram_notification.send_message('test warning message', 'warning')
    context.resources.telegram_notification.send_message('test error message', 'error')
    time.sleep(30)
    return 1


@op()
def goodbye(foo):
    if foo != 1:
        raise Exception("Bad io manager")

    return foo * 2


@job(resource_defs={
    "telegram_notification": telegram_notification,
},
)
def my_job():
    goodbye(hello())


@schedule(cron_schedule="* * * * *", job=my_job, execution_timezone="US/Central")
def my_schedule(_context):
    return {}


@repository
def deploy_docker_repository():
    return [my_job, my_schedule]
