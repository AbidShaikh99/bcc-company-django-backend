from celery import shared_task


@shared_task
def test_celery_task():
    print("CELERY TEST TASK IS WORKING")
    return "Celery task completed successfully"