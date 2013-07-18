import patches, dni


def initialize(context):
    import sys
    try:
        import cs.pfg.dnivalidator.dni
        sys.modules['Products.PloneFormGen.validators.dni'] = cs.pfg.dnivalidator.dni
    except ImportError:
        from logging import getLogger
        log = getLogger('patch')
        log.info('error')




