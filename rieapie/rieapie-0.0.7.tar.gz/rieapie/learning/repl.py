import bpython
import rieapie.learning

def main():
    banner = """
Riapie learning tool.
Use the apis object to access a subclass of Rieapie for each available api.
E.g.
>>> results = search("Alternative to")
>>> results[0].get_help() # will open a browser to the api documentation
>>> results[0].software.firefox.get()
"""
    apis = rieapie.learning.apis

    def search(query):
        results = []
        for el in apis.keys():
            if el.lower().find(query.lower()) >=0 or apis[el].description.lower().find(query.lower()) >= 0:
                results.append(apis[el])
        return results

    bpython.embed(locals_ = locals(), banner = banner)

