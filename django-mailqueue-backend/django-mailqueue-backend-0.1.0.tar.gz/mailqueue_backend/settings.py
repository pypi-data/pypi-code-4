from django.conf import settings

LOG_FILENAME = getattr(settings, 'MAIL_QUEUE_LOG_FILENAME',
    'smtp.mail_queue.mail_queue_fail.log')
LOG_FILE_MAXBYTES = getattr(settings, 'MAIL_QUEUE_LOG_FILE_MAXBYTES',5242880)
LOG_FILE_BACKUP = getattr(settings, 'MAIL_QUEUE_LOG_FILE_BACKUP', 5)

QUEUE_EXPIRE = getattr(settings, 'MAIL_QUEUE_EXPIRE',86400)

QUEUE_NAME = getattr(settings, 'MAIL_QUEUE_NAME','MAIL_QUEUE')