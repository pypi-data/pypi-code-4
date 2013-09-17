from celery.task import task
from statsmodels.robust import stand_mad


@task
def task_mad(data):
    """
    http://statsmodels.sourceforge.net/devel/generated/statsmodels.robust.scale.stand_mad.html
    """

    mad = stand_mad(data)

    return mad
