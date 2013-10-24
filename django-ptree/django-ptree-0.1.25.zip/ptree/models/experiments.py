from django.db import models
import common
from django.template import defaultfilters
import random
from urlparse import urljoin
from django.conf import settings

class BaseExperiment(models.Model):
    """Base class for all Experiments.
    An Experiment is a randomization between Treatments.

    Example:

    You could have 2 Treatments:
    - Prisoner's Dilemma with high payoff (users play for max reward of $5)
    - Prisoner's Dilemma with low payoff (users play for max reward of $1)

    You're interested in seeing how the payoff affects users' behavior.

    So, you define those 2 Treatments,
    and then create an Experiment that randomly assigns users to one or the other.
    """

    description = models.TextField(max_length = 1000, null = True, blank = True)
    code = common.RandomCharField(length=8)
    was_paid_through_ptree = models.BooleanField(verbose_name='Was paid through pTree')

    def mturk_start_url(self):
        """The URL that a user is redirected to in order to start a treatment"""
        return urljoin(settings.DOMAIN,
                       '/{}/GetTreatmentOrParticipant/?{}={}'.format(self.url_base,
                                                          common.Symbols.experiment_code_obfuscated,
                                                          self.code))


    def weighted_randomization_choice(self, choices):
       total = sum(w for c, w in choices)
       r = random.uniform(0, total)
       upto = 0
       for c, w in choices:
          if upto + w > r:
             return c
          upto += w

    def pick_treatment_for_incoming_participant(self):
        """pick a treatment according to randomization algorithm."""
        choices = [(treatment, treatment.randomization_weight) for treatment in self.treatments()]
        treatment = self.weighted_randomization_choice(choices)
        return treatment

    def treatments(self):
        return self.treatment_set.all()

    def participants(self):
        return self.participant_set.all()

    class Meta:
        abstract = True