from celery.task import task
from numpy import array
from scipy.stats import friedmanchisquare


@task
def task_friedman(dataOne, dataTwo, dataThree):
    """
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.friedmanchisquare.html
    """

    chi, pvalue = friedmanchisquare(array(dataOne),
                               array(dataTwo), array(dataThree))

    return chi, pvalue
