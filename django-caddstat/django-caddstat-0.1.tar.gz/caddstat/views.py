"""
CADD Stat views
"""

from django.core.mail import send_mail
from django.shortcuts import render
from django.template import loader

from .forms import FeedbackForm, OneColumnForm, TwoColumnForm, ThreeColumnForm
import settings as caddstat_settings
from .tasks import (task_mad, task_tau, task_pearson, task_cohen,
                    task_paired_t, task_mannwhitneyu, task_friedman,
                    task_cohen_kappa)


def start(request):
    """
    CADD Stat homepage
    :param request:
    :return:
    """

    return render(request, 'caddstat/start.html')


def feedback(request):
    """
    Tell us what you think
    """
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():

            c = {
                'name': form.cleaned_data['name'],
                'message': form.cleaned_data['message']
            }
            subject = 'CADD Stat feedback from {0}'.format(
                form.cleaned_data['name'])
            # Email subject *must not* contain newlines
            subject = ''.join(subject.splitlines())
            text_content = loader.render_to_string(
                'caddstat/emails/feedback.txt', c)
            send_mail(subject, text_content, form.cleaned_data['email'],
                      [caddstat_settings.CADDSTAT_FEEDBACK_EMAIL])

            return render(request, 'caddstat/feedbackthanks.html')

    else:
        form = FeedbackForm()

    return render(request, 'caddstat/feedback.html', {'form': form})


def about(request):
    """
    Enrichment error statistics
    :param request:
    :return:
    """

    return render(request, 'caddstat/about.html')


def mad(request):
    """
    MAD statistics
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = OneColumnForm(request.POST)
        if form.is_valid():

            result = task_mad(form.cleaned_data['columnData'])

            return render(request, 'caddstat/madresults.html', {'mad': result})

    else:
        form = OneColumnForm()

    return render(request, 'caddstat/mad.html', {'form': form})


def friedman(request):
    """
    Friedman statistics
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = ThreeColumnForm(request.POST)
        if form.is_valid():

            result = task_friedman(
                form.cleaned_data['columnOneData'],
                form.cleaned_data['columnTwoData'],
                form.cleaned_data['columnThreeData']
            )

            return render(request, 'caddstat/friedmanresults.html',
                          {'chi': result[0], 'pvalue': result[1]})

    else:
        form = ThreeColumnForm()

    return render(request, 'caddstat/friedman.html', {'form': form})


def mwu(request):
    """
    Mann-Whitney U statistics
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = TwoColumnForm(request.POST)
        if form.is_valid():

            result = task_mannwhitneyu(
                form.cleaned_data['columnOneData'],
                form.cleaned_data['columnTwoData']
            )

            return render(request, 'caddstat/mwuresults.html',
                          {'uvalue': result[0], 'pvalue': result[1]})

    else:
        form = TwoColumnForm()

    return render(request, 'caddstat/mwu.html', {'form': form})


def kappa(request):
    """
    Kappa statistics
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = TwoColumnForm(request.POST)
        if form.is_valid():

            result = task_cohen_kappa(
                form.cleaned_data['columnOneData'],
                form.cleaned_data['columnTwoData']
            )

            return render(request, 'caddstat/kapparesults.html',
                          {'kappa': result})

    else:
        form = TwoColumnForm()

    return render(request, 'caddstat/kappa.html', {'form': form})


def tau(request):
    """
    Tau statistics
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = TwoColumnForm(request.POST)
        if form.is_valid():

            result = task_tau(
                form.cleaned_data['columnOneData'],
                form.cleaned_data['columnTwoData']
            )

            return render(request, 'caddstat/tauresults.html',
                          {'tau': result[0], 'pvalue': result[1]})

    else:
        form = TwoColumnForm()

    return render(request, 'caddstat/tau.html', {'form': form})


def pearson(request):
    """
    Pearson statistics
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = TwoColumnForm(request.POST)
        if form.is_valid():

            result = task_pearson(
                form.cleaned_data['columnOneData'],
                form.cleaned_data['columnTwoData']
            )

            return render(request, 'caddstat/pearsonresults.html',
                          {'rvalue': result[0], 'pvalue': result[1]})

    else:
        form = TwoColumnForm()

    return render(request, 'caddstat/pearson.html', {'form': form})


def ttest(request):
    """
    Paired t-test
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = TwoColumnForm(request.POST)
        if form.is_valid():

            result = task_paired_t(
                form.cleaned_data['columnOneData'],
                form.cleaned_data['columnTwoData']
            )

            return render(request, 'caddstat/ttestresults.html',
                          {'tvalue': result[0], 'pvalue': result[1]})

    else:
        form = TwoColumnForm()

    return render(request, 'caddstat/ttest.html', {'form': form})


def effectsize(request):
    """
    Effect size statistics
    :param request:
    :return:
    """

    if request.method == 'POST':
        form = TwoColumnForm(request.POST)
        if form.is_valid():

            result = task_cohen(
                form.cleaned_data['columnOneData'],
                form.cleaned_data['columnTwoData']
            )

            return render(request, 'caddstat/effectsizeresults.html',
                          {'effectsize': result})

    else:
        form = TwoColumnForm()

    return render(request, 'caddstat/effectsize.html', {'form': form})
