from django.conf import settings



TEST_EMAIL_ADDRESS = getattr(settings, 'TEST_EMAIL_ADDRESS', 'test@test.cz')
COUNT_MAILS_IN_BATCH = getattr(settings, 'COUNT_MAILS_IN_BATCH', 10)
COUNT_DAYS_TO_DELETE_MAIL = getattr(settings, 'COUNT_DAYS_TO_DELETE_MAIL', 7)
