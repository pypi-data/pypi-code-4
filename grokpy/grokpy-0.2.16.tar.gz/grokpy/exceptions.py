'''
Base exceptions for the Grok Client Library
'''

class GrokError(Exception):
  pass

class AuthenticationError(GrokError):
  pass
