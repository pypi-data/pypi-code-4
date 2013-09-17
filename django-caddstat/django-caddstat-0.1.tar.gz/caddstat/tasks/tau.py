from celery.task import task
from scipy.stats import kendalltau


@task
def task_tau(dataOne, dataTwo):
    """
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html
    """

    tau, pvalue = kendalltau(dataOne, dataTwo)

    return tau, pvalue
