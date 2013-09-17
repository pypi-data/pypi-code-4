from celery.task import task
from scipy.stats import mannwhitneyu


@task
def task_mannwhitneyu(dataOne, dataTwo):
    """
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html
    """

    uvalue, pvalue = mannwhitneyu(dataOne, dataTwo)

    return uvalue, pvalue
