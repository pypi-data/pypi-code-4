

class ExtractionOutput(object):
    def __init__(self, filename):
        self.filename = filename
    
    def read(self):
        return open(self.filename).read()



class MessageExtractor(object):
    def __init__(self, client, project=None):
        self.client = client
        self.project = None
        
    def set_sources(self, sources):
        self.sources = sources
        
    def extract(self):
        java_sourcefiles = self.client.new_list()
        
        for source in self.sources:
            java_sourcefiles.append(source.build_sourcefile(self.client))
            
        file = self.client.gateway.extractMessages(java_sourcefiles, self.project)
        return ExtractionOutput(file)
