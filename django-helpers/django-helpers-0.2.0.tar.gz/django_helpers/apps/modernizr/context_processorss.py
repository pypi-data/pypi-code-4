def modernizer(request):
    return {
        'modernizr': request.modernizr or False
    }