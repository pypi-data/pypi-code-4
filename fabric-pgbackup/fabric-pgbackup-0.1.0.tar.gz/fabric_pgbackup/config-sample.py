PG_BACKUP_CONF = {
    'SSH': {
        'SOURCE': 'user@example.com:123',  # leave blank if running locally
        'TARGET': '',  # leave blank if same as source
    },
    'DATABASES': {
        'SOURCE': {
            'HOST': '127.0.0.1',
            'NAME': 'dbname',
            'PORT': 5432,
            'USER': 'joe',
            'PASSWORD': '',
        },
        'TARGET': {
            'HOST': '',
            'NAME': '',
            'PORT': 5432,
            'USER': '',
            'PASSWORD': '',
        },
    },
    'BACKUP_FILES_LOCATION': '~/backups/',
}
