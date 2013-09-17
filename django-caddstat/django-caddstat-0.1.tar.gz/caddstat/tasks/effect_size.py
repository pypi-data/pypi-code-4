from celery.task import task
from numpy import mean, std, sqrt, fabs
from pandas import DataFrame


@task
def task_cohen(dataOne, dataTwo):

    labelOne = 'column1'
    labelTwo = 'column2'

    # Create input
    df = DataFrame.from_items([(labelOne, dataOne), (labelTwo, dataTwo)])

    meanx = mean(df[labelOne])
    meany = mean(df[labelTwo])
    sdx = std(df[labelOne])
    sdy = std(df[labelTwo])
    s = sqrt((sdx**2 + sdy**2)/2)
    d = round(fabs(meanx-meany)/s, 4)

    return d
