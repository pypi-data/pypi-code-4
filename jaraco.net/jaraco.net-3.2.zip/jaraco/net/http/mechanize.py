import logging

import requests
import lxml

log = logging.getLogger(__name__)

class PageGetter(object):
	"""
	PageGetter
	A helper class for common HTTP page retrieval.
	"""

	def __init__(self):
		"initialize the session"
		self.session = requests.Session()

	def open_for_lxml(self, method, url, values):
		"""
		Open a request for lxml using the session
		"""
		return self.session.request(url=url, method=method, data=dict(values))

	@classmethod
	def submit(cls, form):
		return lxml.html.submit_form(form, open_http=cls.open_for_lxml)

	def load(self, url):
		return self.session.get(url)

	def process_form(self, resp, form_data):
		page = lxml.html.fromstring(resp.text, base_url=resp.url)
		form = self.select_form(page.forms)
		self.fill_form(form, form_data)
		return self.submit(form)

	def select_form(self, forms):
		sel = getattr(self, 'form_selector', 0)
		log.info('selecting form %s', sel)
		if not isinstance(sel, int):
			# assume the selector is the name of the form
			forms = dict(map(lambda f: (f.name, f), forms))
		return forms[sel]

	def fill_form(self, form, data):
		for name, value in data.items():
			if callable(value):
				value = value()
			form.fields[name] = value
