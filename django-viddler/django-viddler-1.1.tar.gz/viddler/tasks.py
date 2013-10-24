from celery import task


@task()
def update_viddler(video_id, **kwargs):
    pass
