class OnceRecordMode(object):
    def should_record(request, cassette):
        if not cassette.write_protected:
	    return True
        return False

    def should_play(request, cassette):
        return True
        
class NewEpisodesRecordMode(object):
    def should_record(request, cassette):
	return True

    def should_play(request, cassette):
        return True

class NoneRecordMode(object):
    def should_record(request, cassette):
	return False

    def should_play(request, cassette):
        return True

class AllRecordMode(object):
    def should_record(request, cassette):
	return False

    def should_play(request, cassette):
        return True

