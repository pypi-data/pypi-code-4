from itertools import izip_longest
import re

from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

FILE_BOUNDARY_RE = re.compile(r'^-- title=(\w+).*$', re.MULTILINE)

# grouper recipe: http://docs.python.org/2/library/itertools.html#recipes
def grouper(iterable, n, fillvalue=None):
	"Collect data into fixed-length chunks or blocks"
	# grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
	args = [iter(iterable)] * n
	return izip_longest(fillvalue=fillvalue, *args)

def split_template_file(template_name, context):
	template = render_to_string(template_name, context)

	# split the rendered file and remove empty entries (usually the first entry
	# in the list is empty). also strip each entry of extra newlines --- they
	# improve readability in the original file but will make the end message
	# confusing
	entries = FILE_BOUNDARY_RE.split(template)
	entries = filter(None, entries)
	entries = map(lambda x: x.strip(), entries)

	template_contents = dict(grouper(entries, 2))
	return template_contents

def send_email(template_name, context, to, from_email=settings.DEFAULT_FROM_EMAIL):
	template_contents = split_template_file(template_name, context)

	subject = template_contents['subject']
	msg_txt = template_contents['txt']

	# remove subject newlines before continuing
	subject = ''.join(subject.splitlines())
	email = EmailMultiAlternatives(subject, msg_txt, from_email, [to])

	# attach a text/html part if it exists
	if 'html' in template_contents:
		email.attach_alternative(template_contents['html'], 'text/html')

	email.send()
