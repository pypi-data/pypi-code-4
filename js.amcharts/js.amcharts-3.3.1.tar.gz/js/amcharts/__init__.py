from fanstatic import Library, Resource, get_needed


library = Library('amcharts', 'resources')

css = Resource(library, 'style.css')
amcharts = Resource(library, 'amcharts.js', depends=[css])
amstock = Resource(library, 'amstock.js', depends=[css])


def find_images_url():
    needed = get_needed()
    library_url = needed.library_url(library)
    return '%s/images/' % library_url


