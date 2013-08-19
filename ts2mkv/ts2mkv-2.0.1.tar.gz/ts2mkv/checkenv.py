import re
import process
import ConfigParser

import common

def check_env():
    print 'modules_path:', common.modules_path()
    print

    p = process.Process()

    def check_executable(executable, command):
        try:
            print '  %s' % (executable),
            ''.join(p.execute_as_generator(command))
            print '-> ok'
        except Exception:
            print '-> FAILED!!!'
            return False
        return True

    print 'Checking existence of external programs:'
    avconv_found = check_executable('avconv', 'avconv -version')
    check_executable('java', 'java -version')
    check_executable('mkvinfo', 'mkvinfo --version')
    check_executable('mkvmerge', 'mkvmerge --version')
    check_executable('mkvextract', 'mkvextract --version')

    print
    if avconv_found:
        print 'Checking codecs:'
        codecs = ''.join(p.execute_as_generator('avconv -codecs'))
        def check_codec(codec):
            print '  %s' % (codec),
            if re.search('\s+%s\s+' % (codec), codecs):
                print '-> ok'
            else:
                print '-> FAILED!!!'
        check_codec('mp2')
        check_codec('mpeg2video')
        check_codec('aac')
        check_codec('ac3')
        check_codec('libmp3lame')
        check_codec('libx264')
    else:
        print 'WARNING: Codec check skipped because avconv failed!'

def print_presets():
    for preset_name, fname in [('video', 'videopresets.ini'), ('audio', 'audiopresets.ini')]:
        print 'Available %s presets:' % (preset_name)
        config = ConfigParser.ConfigParser()
        config.read(common.config_files(fname))
        for section in config.sections():
            if config.has_option(section, 'comment'):
                comment = config.get(section, 'comment')
            else:
                comment = '-'
            print '  %s%s%s' % (section, ' ' * (15 - len(section)), comment)
        print

def video_preset_found(preset):
    config = ConfigParser.ConfigParser()
    config.read(common.config_files('videopresets.ini'))
    return preset == '' or config.has_section(preset)

def audio_preset_found(preset):
    config = ConfigParser.ConfigParser()
    config.read(common.config_files('audiopresets.ini'))
    return preset == '' or config.has_section(preset)

if __name__ == '__main__':
    check_env()
    print
    print_presets()
    print video_preset_found('h264')
    print video_preset_found('')
    print video_preset_found('dummy')
