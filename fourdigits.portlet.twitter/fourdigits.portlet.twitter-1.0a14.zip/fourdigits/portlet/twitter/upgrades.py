PROFILE_ID = 'profile-fourdigits.portlet.twitter:default'


def run_all_steps(context):
    context.runAllImportStepsFromProfile(PROFILE_ID, purge_old=False)
