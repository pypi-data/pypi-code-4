from lxml import etree

def trace(msg):
	#print msg
	pass

class PyJath(object):

	def parse(self, template, xml):
		if type(template) == dict:
			return self.parse_dict(template, xml)

		elif type(template) == list:
			return self.parse_list(template, xml)

		else:
			return self.parse_item(template, xml)

	def parse_list(self, template, xml):
		trace('parsing list')	
		retval = []
		r = xml.xpath(template[0])
		for i in range(0, len(r)):
			retval.append(self.parse(template[1], r[i]))
			
		return retval

	def parse_dict(self, template, xml):
		trace('parsing dict')	
		retval = {}
		for item in template:
			retval[item] = self.parse(template[item], xml)
		return retval

	def parse_item(self, template, xml):
		trace('parsing item')	
		node = xml.xpath(template)
		return node[0] or node[0].text

