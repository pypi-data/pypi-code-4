from django import template

# from http://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

register = template.Library()

@register.filter(name='getkey')
def getkey(value, arg):
    ''' Gets a value from a dict by key.  This allows keys to contain spaces, dashes, etc. '''
    return value[arg]
