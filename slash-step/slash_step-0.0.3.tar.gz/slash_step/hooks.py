from slash import hooks

step_start = hooks.ensure_custom_hook('step_start')
step_success = hooks.ensure_custom_hook('step_success')
step_error = hooks.ensure_custom_hook('step_error')
step_end = hooks.ensure_custom_hook('step_end')
