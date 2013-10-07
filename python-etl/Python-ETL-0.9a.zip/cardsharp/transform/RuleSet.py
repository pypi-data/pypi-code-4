
__all__ = ['regions', 'Region', 'get_region']

rule_set = ['al', 'ak', 'az', 'ar', 'ca', 'co', 'ct', 'de', 'dc', 'fl', 'ga', 
          'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md', 'ma', 
          'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nb', 'nb|ne', 'nv', 'nh', 'nj', 
          'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 
          'tn', 'tx', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy', 'wvfbi', 
          'ncic', 'unknown']

#to apply global rules do not return a value on region function
class RuleSet(object):
    def __init__(self, filter, delimiter):
        """
        filter[0] = variable to filter on
        filter[1] = list of values to check variable value against
        delimiter = delimiter value associated with dataset save delimiter (this will have potential 
        logic bug for drivers without a delimiter)
        """
        self.filter_variable = filter[0]
        self.filter_values = filter[1].lower().split(delimiter)
        
    def __str__(self):
        return str(''.join(self.filter_variable, str(self.filter_values)))
    
    def priority(self, priority):
        return priority
    
    def get_filter(self):
        return self.filter
        
def get_ruleset(region, ):
    region = region.lower()
    if region in regions:
        return regions[region]
        
    raise RuleParsingError('Unknown region: %r' % region)

regions = dict((st, Region(st)) for st in regions)