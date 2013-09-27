from pkg_resources import require, DistributionNotFound, VersionConflict

    ## conflicts = []
    ## for req in REQUIRES:
    ##     try:
    ##         require(req)
    ##     except (DistributionNotFound, VersionConflict) as e:
    ##         msg = '%s: %s' % (type(e).__name__, e)
    ##         if msg not in conflicts:
    ##             conflicts.append(msg)
    ## if conflicts:
    ##     for c in conflicts:
    ##         sys.stderr.write('*** %s\n' % c)
    ##     sys.exit(1)
