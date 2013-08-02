"""
            form: [forms+'editable-form-bootstrap.js'],
            container: [containers+'editable-popover.js'],
            inputs: [
                inputs+'date/bootstrap-datepicker/js/bootstrap-datepicker.js',
                inputs+'date/date.js',
                inputs+'date/datefield.js',
                inputs+'datetime/datetime.js',
                inputs+'datetime/datetimefield.js',
                //don't build datetime lib, should be included manually
                //inputs+'datetime/bootstrap-datetimepicker/js/bootstrap-datetimepicker.js',
                inputs+'typeahead.js'
                ],
            css: [
                inputs+'date/bootstrap-datepicker/css/datepicker.css'
               //don't build datetime lib, should be included manually
               //inputs+'datetime/bootstrap-datetimepicker/css/datetimepicker.css'
                ]



                    var js = [
    '<banner:meta.banner>',
    forms+'editable-form.js',
    forms+'editable-form-utils.js',
    containers+'editable-container.js',
    containers+'editable-inline.js',
    lib+'element/editable-element.js',
    inputs+'abstract.js',
    inputs+'list.js',
    inputs+'text.js',
    inputs+'textarea.js',
    inputs+'select.js',
    inputs+'checklist.js',
    inputs+'html5types.js',
    inputs+'select2/select2.js',
    inputs+'combodate/lib/combodate.js',
    inputs+'combodate/combodate.js'
    ]
        var css = [
    '<banner:meta.banner>',
    forms+'editable-form.css',
    containers+'editable-container.css',
    lib+'element/editable-element.css'
    ];


    lib = 'src/'
    forms = lib+'editable-form/'
    inputs = lib+'inputs/'
    containers = lib+'containers/'
"""

from django_helpers.apps.static_manager import jQueryURL, BootstrapURL, AjaxCsrfURL

_lib = 'editable/'
_forms_dir = _lib + 'editable-form/'
_inputs_dir = _lib + 'inputs/'
_containers_dir = _lib + 'containers/'


# noinspection PyUnusedLocal
def _require(css, *js):
    arr = []
    for folder in js:
        for f in folder:
            arr.append(f)
        #
    # if css is not None:
    #     for f in css:
    #         add_css_file(f)

    return arr


def require():
    form = [
        jQueryURL,
        BootstrapURL,
        AjaxCsrfURL,
        _forms_dir + 'editable-form-bootstrap.js'
    ]

    container = [_containers_dir + 'editable-popover.js']

    input_files = [
    ]

    css = [
        _forms_dir + 'editable-form.css',
        _containers_dir + 'editable-container.css',
        _lib + 'element/editable-element.css'
    ]

    js = [
        _forms_dir + 'editable-form.js',
        _forms_dir + 'editable-form-utils.js',
        _containers_dir + 'editable-container.js',
        _containers_dir + 'editable-inline.js',
        _lib + 'element/editable-element.js',
        _inputs_dir + 'abstract.js',
        _inputs_dir + 'list.js',
        _inputs_dir + 'text.js',
        _inputs_dir + 'textarea.js',
        _inputs_dir + 'select.js',
        _inputs_dir + 'checklist.js',
        _inputs_dir + 'html5types.js',
        _inputs_dir + 'select2/select2.js',
        _inputs_dir + 'combodate/lib/combodate.js',
        _inputs_dir + 'combodate/combodate.js'
    ]

    extras = [
        _lib + 'django.xeditable.js'
    ]

    return _require(css, js, form, container, input_files, extras)


def require_date_filed():
    js = [
        jQueryURL,
        BootstrapURL,
        'js/bootstrap-datepicker.js',
        _inputs_dir + 'date/date.js',
        _inputs_dir + 'date/datefield.js',
    ]
    _require(None, js)
