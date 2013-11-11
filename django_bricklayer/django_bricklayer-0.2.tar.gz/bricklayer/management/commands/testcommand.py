from django.core.management.base import BaseCommand
# Uncomment the next line for extending option list
# from optparse import make_option
from bricklayer.utils import SUCCESS_MESSAGE


class Command(BaseCommand):
    help = 'Help text goes here'
    # Uncomment the lines below for extending option list
    # option_list = BaseCommand.option_list + (
    #     make_option('--models', '-m', 
    #                 dest='models', 
    #                 type="string",
    #                 default=None,
    #                help='Model name'),
    # )
    def handle(self, *args, **options):
        from django.core.management import get_commands
        a = get_commands()
        self.stdout.write(str(a), SUCCESS_MESSAGE)
        