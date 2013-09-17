from celery.task import task
from sklearn.metrics import confusion_matrix
from statsmodels.stats.inter_rater import cohens_kappa


@task
def task_cohen_kappa(dataOne, dataTwo):
    """
    http://statsmodels.sourceforge.net/devel/generated/statsmodels.stats.inter_rater.cohens_kappa.html
    """

    kappa = cohens_kappa(confusion_matrix(dataOne, dataTwo))

    clean_kappa = str(kappa).replace('              ', '')

    return clean_kappa
