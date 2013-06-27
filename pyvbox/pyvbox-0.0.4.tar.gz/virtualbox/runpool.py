from virtualbox import manage








class ClonePool(object):

    def __init__(self, name_or_id, size, **guest_session_kwargs):

        # create temp clones
        clones = []
        for i in range(size):
            vm_clone = manage.temp_clonevm(name_or_id)
            manage.startvm(vm_clone, 'headless')
            clones.append(vm_clone)
            
        # wait for clones to boot than take an initialised snapshot
        for clone in clones:
            print("Initialising %s" % clone.name)
            with manage.guess_session_context(clone, 
                                    **guest_session_kwargs) as gs:
                pass
            manage.snapshot_take(clone, 'initialised')
            manage.snapshot_restore(clone, 'initialised')



