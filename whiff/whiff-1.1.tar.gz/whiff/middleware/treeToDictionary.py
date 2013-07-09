whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/treeToDictionary - translate an "embedded" tree into flattened form
{{/include}}

The <code>whiff_middleware/treeToDictionary</code>
middleware translates a tree encoded in JSON like this
{{include "javascript"}}
	{ "id": "general",
	  "body": "<a href='http:www.wikipedia.com'>general studies</a>",
	  "children": [
		{ "id" : "liberal arts",
		  "body" : "<a href='http://www.bmcc.cuny.edu/liberalarts/'>liberal arts: the study of humanities</a>",
		  "children": [
		  		{ "id" : "literature",
				  "body" : "literature: the study of writings"
				},
				{ "id" : "ethics",
				  "body" : "ethics: the study of right and wrong"
				}
			]
		},
	  	{ "id" : "fine arts",
		  "body" : "<a href='http://www.fineartlamps.com/'>fine arts: the study of beauty and creativity</a>",
		  "children": [
		  		{ "id" : "sculpture",
				  "body" : "sculpture: the study of artistic expression in three dimensional forms"
				},
				{ "id" : "music",
				  "body" : "music: the study of artistic expression using sounds"
				}
			]
		},
		{ "id" : "science",
		  "body" : "<a href='http://www.scientificamerican.com/'>science: the study of the physical properties of things</a>",
		  "children": [
		  		{ "id" : "physics",
				  "body" : "physics: the study of the behaviour and interaction of non-living objects"
				},
				{ "id" : "biology",
				  "body" : "<a href='http://www.profishservices.com/Bio.htm'>biology: the study of living things</a>"
				}
			]
		},
		{ "id" : "engineering",
		  "body" : "<a href='http://www.menloeng.com/'>engineering: the study of how to make things work.</a>",
		  "children": [
		  		{ "id" : "civil engineering",
				  "body" : "civil engineering: the study of how to build civic infrastructures"
				},
				{ "id" : "electrical engineering",
				  "body" : "electrical engineering: the study of the use of electricity"
				}
			]
		}
	  ]
	}
{{/include}}
into a "flattened" dictionary representation, like this
{{include "javascript"}}
    {{include "whiff_middleware/treeToDictionary"}}
	{ "id": "general",
	  "body": "<a href='http:www.wikipedia.com'>general studies</a>",
	  "children": [
		{ "id" : "liberal arts",
		  "body" : "<a href='http://www.bmcc.cuny.edu/liberalarts/'>liberal arts: the study of humanities</a>",
		  "children": [
		  		{ "id" : "literature",
				  "body" : "literature: the study of writings"
				},
				{ "id" : "ethics",
				  "body" : "ethics: the study of right and wrong"
				}
			]
		},
	  	{ "id" : "fine arts",
		  "body" : "<a href='http://www.fineartlamps.com/'>fine arts: the study of beauty and creativity</a>",
		  "children": [
		  		{ "id" : "sculpture",
				  "body" : "sculpture: the study of artistic expression in three dimensional forms"
				},
				{ "id" : "music",
				  "body" : "music: the study of artistic expression using sounds"
				}
			]
		},
		{ "id" : "science",
		  "body" : "<a href='http://www.scientificamerican.com/'>science: the study of the physical properties of things</a>",
		  "children": [
		  		{ "id" : "physics",
				  "body" : "physics: the study of the behaviour and interaction of non-living objects"
				},
				{ "id" : "biology",
				  "body" : "<a href='http://www.profishservices.com/Bio.htm'>biology: the study of living things</a>"
				}
			]
		},
		{ "id" : "engineering",
		  "body" : "<a href='http://www.menloeng.com/'>engineering: the study of how to make things work.</a>",
		  "children": [
		  		{ "id" : "civil engineering",
				  "body" : "civil engineering: the study of how to build civic infrastructures"
				},
				{ "id" : "electrical engineering",
				  "body" : "electrical engineering: the study of the use of electricity"
				}
			]
		}
	  ]
	}
    {{/include}}
{{/include}}

"""

from whiff.middleware import misc
from whiff import gateway

class treeToDictionary(misc.utility):
    def __init__(self, page, toResource=None):
        self.page = page
        self.toResource = toResource
    def __call__(self, env, start_response):
        toResource = self.param_json(self.toResource, env)
        inDict = self.param_json(self.page, env)
        (outDict, rootname) = self.translate(inDict)
        if toResource is not None:
            # store dict at resource and return empty string
            gateway.putResource(env, toResource, outDict)
            return self.deliver_page("", env, start_response)
        else:
            # return dict as encoded as json
            return self.deliver_json(outDict, env, start_response)
    def translate(self, inDict, outDict=None, parentName=None):
        if outDict is None:
            outDict = {}
        name = inDict["id"]
        body = inDict["body"]
        children = inDict.get("children", ())
        childNames = []
        for child in children:
            (outDict, childname) = self.translate(child, outDict, name)
            childNames.append(childname)
        nodeDict = {}
        nodeDict["body"] = body
        if parentName:
            nodeDict["parent"] = parentName
        if childNames:
            nodeDict["children"] = childNames
        outDict[name] = nodeDict
        return (outDict, name)

__middleware__ = treeToDictionary

SAMPLEINPUT = """
	{ "id": "general",
	  "body": "<a href='http:www.wikipedia.com'>general studies</a>",
	  "children": [
		{ "id" : "liberal arts",
		  "body" : "<a href='http://www.bmcc.cuny.edu/liberalarts/'>liberal arts: the study of humanities</a>",
		  "children": [
		  		{ "id" : "literature",
				  "body" : "literature: the study of writings"
				},
				{ "id" : "ethics",
				  "body" : "ethics: the study of right and wrong"
				}
			]
		},
	  	{ "id" : "fine arts",
		  "body" : "<a href='http://www.fineartlamps.com/'>fine arts: the study of beauty and creativity</a>",
		  "children": [
		  		{ "id" : "sculpture",
				  "body" : "sculpture: the study of artistic expression in three dimensional forms"
				},
				{ "id" : "music",
				  "body" : "music: the study of artistic expression using sounds"
				}
			]
		},
		{ "id" : "science",
		  "body" : "<a href='http://www.scientificamerican.com/'>science: the study of the physical properties of things</a>",
		  "children": [
		  		{ "id" : "physics",
				  "body" : "physics: the study of the behaviour and interaction of non-living objects"
				},
				{ "id" : "biology",
				  "body" : "<a href='http://www.profishservices.com/Bio.htm'>biology: the study of living things</a>"
				}
			]
		},
		{ "id" : "engineering",
		  "body" : "<a href='http://www.menloeng.com/'>engineering: the study of how to make things work.</a>",
		  "children": [
		  		{ "id" : "civil engineering",
				  "body" : "civil engineering: the study of how to build civic infrastructures"
				},
				{ "id" : "electrical engineering",
				  "body" : "electrical engineering: the study of the use of electricity"
				}
			]
		}
	  ]
	}
"""

def test():
    app = treeToDictionary(SAMPLEINPUT)
    result = list(app({}, misc.ignore))
    print "".join(result) # verbose

if __name__=="__main__":
    test()
