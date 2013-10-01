from swingers import models
from swingers.models import ActiveModel, Audit


class Duck(Audit):
    """A duck."""
    name = models.CharField(max_length=20)


class ActiveDuck(ActiveModel):
    """An active duck."""
    name = models.CharField(max_length=20)


class ParentDuck(Audit):
    """A parent duck."""
    name = models.CharField(max_length=20)
    duck = models.ForeignKey(Duck)


class GrandParentDuck(Audit):
    """A parent duck."""
    name = models.CharField(max_length=20)
    duck = models.ForeignKey(ParentDuck)
