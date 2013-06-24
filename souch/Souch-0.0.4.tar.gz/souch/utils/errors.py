from colors import bcolors

class CouchDBOff(Exception):
    def __init__(self, value, value2, color):
        self.value = value
        self.value2 = value2
        color = getattr(bcolors, color)
        self.complete_string = color + "%s %s" %(self.value, self.value2) + bcolors.ENDC
    def __str__(self):
        print ("\n %s" % self.complete_string)
