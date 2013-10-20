import logging
from pyage.core.inject import InjectOptional
from pyage.core.migration import  Pyro4Migration

logger = logging.getLogger(__name__)

class CountingPyro4Migration(Pyro4Migration):

    counter = 0

    @InjectOptional("migration_probability")
    def __init__(self):
        if hasattr(self, "migration_probability"):
            probability = self.migration_probability
        else:
            probability = 0.05
        super(CountingPyro4Migration, self).__init__(probability)

    def migrate(self, agent):
        if super(CountingPyro4Migration, self).migrate(agent):
            CountingPyro4Migration.counter += 1
            logging.info("migrated!")



