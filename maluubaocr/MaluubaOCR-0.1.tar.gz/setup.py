try:
    from setuptools import setup
except ImportError:
    from disutils.core import setup

config = {
    'description': 'Maluuba OCR',
    'author': 'Maluuba',
    'url': 'http://maluuba.com',
    'download_url': 'http://github.com/Maluuba/InterviewQuestions',
    'author_email': 'adrian.petrescu@maluuba.com',
    'version': '0.1',
    'install_requires': ['nose', 'arff'],
    'packages': ['MaluubaOCR'],
    'scripts': [],
    'name': 'MaluubaOCR'
}

setup(**config)
