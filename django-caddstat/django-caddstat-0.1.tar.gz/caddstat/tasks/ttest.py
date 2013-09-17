from celery.task import task
from scipy.stats import ttest_rel


@task
def task_paired_t(dataOne, dataTwo):
    """
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html
    """

    tvalue, pvalue = ttest_rel(dataOne, dataTwo)

    return tvalue, pvalue
