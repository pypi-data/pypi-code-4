from celery.task import task
from scipy.stats import pearsonr


@task
def task_pearson(dataOne, dataTwo):
    """
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
    """

    rvalue, pvalue = pearsonr(dataOne, dataTwo)

    return rvalue, pvalue
