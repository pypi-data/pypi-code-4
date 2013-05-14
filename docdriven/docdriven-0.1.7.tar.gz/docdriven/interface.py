import json
import datetime
import string
import os
import re

driven_doc = None

# text sections
EN_PRE_CONFIG = 0
CONFIG = 1
EN_POST_CONFIG = 2
PREDICT = 3
EN_POST_PREDICT = 4
RESPONSE = 5
EN_POST_RESPONSE =6
RUNTIME = 7
EN_POST_RUNTIME = 8
STATUS = 9
EN_POST_STATUS = 10

# other sections
CHAPTER = 20

class StatusReport(object):
    def __init__(self, code='BLANK', level=6, timestamp=datetime.datetime.now().isoformat(), speed=0.0, note=None):
        self.code = code
        self.level = level
        self.timestamp = timestamp
        self.speed = speed
        self.note = note

    def add_status_stamp(self, code, level, timestamp, speed=None, note=None):
        if level < self.level:
            self.level = level
            self.code = code
            self.timestamp = timestamp
            self.speed = speed
            self.note = note

    def accumulate_route_status(self, status_report):
        if status_report is not None:
            self.speed += status_report['speed']
            if status_report['level'] < self.level:
                self.level = status_report['level']
                self.code = status_report['code']
            self.timestamp = status_report['timestamp']
            if self.note and status_report.get('note'):
                self.note += '\n'+status_report['note']
            elif not self.note and status_report.get('note'):
                self.note = status_report['note']
            elif self.note and not status_report.get('note'):
                pass
            else:
                pass



class AbstractDocUnit(object):

    def __init__(self, title, key_filepath=None):
        self.title = title
        self.CODE = False
        self.CODE_HEADER = False
        self.code_index = -1
        self.text_index = 0
        self.sections = ['','','','','','','','','','',''] # index range is 0 to 10
        self.section_keypaths = ['','','','','','','','','','',''] # index range is 0 to 10
        self.key_filepath = key_filepath
        # self.status_stamps = [


    def get_keypath(self, section):
        if section == CHAPTER:
            if self.key_filepath is not None:
                return self.key_filepath
            else: # should never happen, since key_filepath should always be set
                return title2filename(self.title)
        elif section == CONFIG or section == PREDICT or section == RESPONSE or section == RUNTIME or section == STATUS:
            if len(self.section_keypaths[section])>0:
                return self.section_keypaths[section]
            else:
                if self.__class__.__name__ == 'ChapterDocUnit':
                    return self.key_filepath
                elif self.__class__.__name__ == 'RouteDocUnit':
                    return self.chapter.key_filepath+'.'+self.title2filename(self.title)
                else:
                    raise Exception('Unknown class type: '+self.__class__.__name__)


    def runtime_exec(self, response):
        # print 'ADJUSTING FOR NEXT CONFIG - BEGIN'
        runtime_config = {}
        runtime_reply = {}
        exec self.sections[RUNTIME]
        # print 'ADJUSTING FOR NEXT CONFIG - FINISHED'
        return (runtime_config, runtime_reply)


    def status_stamp(self, code, level, timestamp, speed=0.0, note=None):
        isoformat = timestamp.isoformat()
        self.sections[STATUS] = json.dumps({
            'code':code,
            'level':level,
            'timestamp':isoformat[:10]+' '+isoformat[11:22],
            'speed':speed,
            'note':note
            }, indent=4, separators=(',',':'))

    def get_status_report(self):
        if len(self.sections[STATUS]) > 3:
            return json.loads(self.sections[STATUS])
        else:
            return None

    def write_nav_files(self, chapdir, chapter_file):
        index = EN_PRE_CONFIG
        sects = ['human', 'config', 'human', 'predict', 'human', 'response', 'human', 'runtime', 'human', 'status', 'human']
        for section in self.sections:
            if index % 2 == 1: # if index to sections array is 1, 3, 5, 7, 9, 11, ... then we are dealing with code
                if len(self.sections[index]) > 0:
                    filepath = self.get_keypath(section=index)
                    if index == 7:
                        filepath += '.py'
                    else:
                        filepath += '.json'
                    chapter_file.write('#### '+sects[index]+'/'+filepath.rstrip()+'\n')
                    navdir = os.path.join(chapdir, sects[index])
                    nav_filepath = os.path.join(navdir, filepath)
                    navfile = open(nav_filepath, 'w')
                    if index == 7:
                        navfile.write(self.sections[index]+'\n')
                    else:
                        navfile.write(self.pretty_json(self.sections[index])+'\n')
                    navfile.close()
                else:
                    chapter_file.write('#### '+sects[index]+'/\n') # trailng slash indicates an empty code section
            else: # it is a text file meant for human, not machine consumption, so we write it to the chapter directly
                if len(self.sections[index].rstrip()) > 0:
                    chapter_file.write(self.sections[index].rstrip()+'\n')
            index += 1
            if self.__class__.__name__ == 'ChapterDocUnit' and index > 3:
                break # chapter doc units don't have response, runtime, or status - only routes do


    def as_string(self, response=True, status=True):
        doc_string = ''

        if len(self.sections[EN_PRE_CONFIG]) > 0:
            doc_string += self.sections[EN_PRE_CONFIG]

        if len(self.sections[CONFIG]) > 0:
            doc_string += '\n#### config'
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[CONFIG])
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            doc_string += '\n#### config/\n'

        if len(self.sections[EN_POST_CONFIG]) > 0:
            doc_string += self.sections[EN_POST_CONFIG]

        if len(self.sections[PREDICT]) > 0:
            doc_string += '\n#### predict'
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[PREDICT])
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            doc_string += '\n#### predict/\n'

        if len(self.sections[EN_POST_PREDICT]) > 0:
            doc_string += self.sections[EN_POST_PREDICT]

        if len(self.sections[RESPONSE]) > 0 and response:
            doc_string += '\n#### response'
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[RESPONSE])
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            doc_string += '\n#### response/\n'

        if len(self.sections[EN_POST_RESPONSE]) > 0:
            doc_string += self.sections[EN_POST_RESPONSE]

        if len(self.sections[RUNTIME]) > 2:
            doc_string += '\n#### runtime'
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  python\n'
            doc_string += self.sections[RUNTIME]
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            doc_string += '\n#### runtime/\n'

        if len(self.sections[EN_POST_RUNTIME])>0:
             doc_string += self.sections[EN_POST_RUNTIME]

        if len(self.sections[STATUS]) > 0:
            doc_string += '\n#### status'
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[STATUS])
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            doc_string += '\n#### status/\n'

        if len(self.sections[EN_POST_STATUS])>0:
            doc_string += self.sections[EN_POST_STATUS]

        return doc_string

    def as_ch_status_string(self):
        if len(self.sections[STATUS]) < 1:
            return 'BLANK'.ljust(8)+' '+self.title
        else:
            status_stamp = json.loads(self.sections[STATUS])
            return status_stamp['code'].ljust(8)+' '+self.title

    def pretty_json(self, json_string):
        try:
            pretty = json.dumps(json.loads(json_string), indent=4, separators=(',', ': '))
            return pretty
        except Exception, e:
            print 'invalid json:'
            print json_string
            raise e

    def is_code_header(self, line):
        return True if line.startswith('#### ') else False

    def is_text(self, line):
        return True if not self.CODE else False

    def is_start_code(self, line):
        return True if line.startswith('~~~') and self.CODE_HEADER else False

    def is_end_code(self, line):
        return True if line.startswith('~~~') and self.CODE else False

    def consume_line(self, line, from_filepath):
        if line.startswith(('# ','## ','% ')):
            raise Exception ('cannot consume line: '+line)
        else:
            if self.is_code_header(line):
                self.consume_code_header(line, from_filepath)
            elif self.is_start_code(line):
                self.CODE_HEADER = False
            elif self.is_end_code(line):
                self.CODE = False
                if self.code_index != RUNTIME:
                    self.sections[self.code_index] = self.pretty_json(self.sections[self.code_index])
            elif self.is_text(line):
                self.sections[self.text_index] += line.rstrip()+'\n'
            elif self.CODE:
                self.sections[self.code_index] += line.rstrip()+'\n'
            else:
                raise Exception ('unknown line type: '+line)

    def consume_code_header(self, line, from_filepath):
        self.CODE = True
        this_keypath = self.key_filepath
        if from_filepath != self.key_filepath:
            # this means this code section did not come from the same file as the surrounding docunit
            this_keypath = from_filepath
        self.CODE_HEADER = True
        header = line[5:].strip().lower()
        if header.startswith('config'):
            if self.code_index != -1:
                raise Exception('config section must come before any other code section')
            else:
                self.code_index = 1
                self.text_index = 2
            if header.endswith('config/'):
                self.CODE = False # empty code section just increments the text index counter
        elif header.startswith('predict'):
            if self.code_index > 3:
                raise Exception('predict section cannot be the third (or higher) code section')
            else:
                self.code_index = 3
                self.text_index = 4
            if header.endswith('predict/'):
                self.CODE = False # empty code section just increments the text index counter
        elif header.startswith('response'):
            self.code_index = 5
            self.text_index = 6
            if header.endswith('response/'):
                self.CODE = False # empty code section just increments the text index counter
        elif header.startswith('runtime'):
            self.code_index = 7
            self.text_index = 8
            if header.endswith('runtime/'):
                self.CODE = False # empty code section just increments the text index counter
        elif header.startswith('status'):
            self.code_index = 9
            self.text_index = 10
            if header.endswith('status/'):
                self.CODE = False # empty code section just increments the text index counter
        else:
            raise Exception('invalid code header: '+header+' - must be one of: config, predict, response, status, or runtime')
        self.sections[self.code_index] = ''
        self.section_keypaths[self.code_index] = this_keypath


    def feed_line(self, line, from_filepath):
        self.consume_line(line, from_filepath)



class ChapterDocUnit(AbstractDocUnit):
    def __init__(self, title, key_filepath=None):
        self.current_doc_unit = self
        self.route_list = []
        self.status_report = StatusReport()
        super(ChapterDocUnit, self).__init__(title, key_filepath)

    def feed_line(self, line, from_filepath):
        if line.startswith('# '):
            raise Exception('ChapterDocUnit cannot be fed a chapter title: '+line)
        elif line.startswith('## '):
            assert from_filepath == self.key_filepath
            self.route_list.append(RouteDocUnit(line[3:].strip(), self))
            self.current_doc_unit = self.route_list[-1]
        else:
            self.current_doc_unit.consume_line(line, from_filepath)

    def print_all_to_file(self, outfile, response=True):
        outfile.write('# '+self.title+'\n')
        outfile.write(self.as_string(response))
        for route in self.route_list:
            route.print_all_to_file(outfile, response)

    def print_nav_to_file(self, parent_dir, response=True):
        chapter_filepath = os.path.join(parent_dir, 'chapter/'+self.get_keypath(section=CHAPTER)+'.nav.dd')
        nav_out = open(chapter_filepath, 'w')
        nav_out.write('# '+self.title+'\n')
        self.write_nav_files(os.path.join(parent_dir, 'chapter/'), nav_out)
        for route in self.route_list:
            nav_out.write('## '+route.title+'\n')
            route.write_nav_files(os.path.join(parent_dir, 'chapter/'), nav_out)
        nav_out.close()

    def accumulate_route_status(self):
        self.status_report = StatusReport()
        for route in self.route_list:
            self.status_report.accumulate_route_status(route.get_status_report())
        self.sections[STATUS] = json.dumps({
            'code':self.status_report.code,
            'level':self.status_report.level,
            'timestamp':self.status_report.timestamp,
            'speed':self.status_report.speed,
            'note':self.status_report.note
            }, indent=4, separators=(',',':'))

    def get_json_doc_struct(self):
        struct = {
            "config": json.loads(self.sections[CONFIG]),
            "reply": json.loads(self.sections[PREDICT]),
            "status": json.loads(self.sections[STATUS]),
            "route_list": []
        }
        for route in self.route_list:
            struct['route_list'].append(route.get_json_doc_structure())

    def print_to_ch_status_file(self, ch_status_file):
        self.accumulate_route_status()
        ch_status_file.write(self.as_ch_status_string()+'\n')
        for route in self.route_list:
            ch_status_file.write('         '+route.as_ch_status_string()+'\n')
        ch_status_file.write('\n')



class RouteDocUnit(AbstractDocUnit):
    def __init__(self, title, chapter):
        self.chapter = chapter
        super(RouteDocUnit, self).__init__(title, chapter.key_filepath)

    def print_all_to_file(self, outfile, response=True):
        outfile.write('\n## '+self.title+'\n')
        outfile.write(self.as_string(response))

    def get_json_doc_struct(self):
        return {
            self.title: {
                "config": json.loads(self.sections[CONFIG]),
                "reply": json.loads(self.sections[PREDICT]),
                "response": json.loads(self.sections[RESPONSE]),
                "status": json.loads(self.sections[STATUS]),
                "runtime": json.loads(self.sections[RUNTIME])
            }
        }





class DrivenDoc(object):
    def __init__(self):
        self.title = None
        self.author = None
        self.date = None
        self.introduction = None
        self.chapter_list = []
        self.conclusion = None
        self.current_chapter = None
        self.chapter_set = set()
        self.route_dict = {}
        self.chapter_count = 0
        self.route_count = 0

    def get_json_doc_structure(self):
        doc_struct = {}
        doc_struct['title'] = self.title
        doc_struct['date'] = self.date
        doc_struct['author'] = self.author
        if self.introduction:
            doc_struct['introduction'] = self.introduction.get_json_doc_structure()
        for chapter in self.chapter_list:
            doc_struct[chapter.title] = chapter.get_json_doc_structure()
        if self.conclusion:
            doc_struct['conclusion'] = self.conclusion.get_json_doc_structure()


    def print_all_to_file(self, outfile, response=True):
        # print "I've been asked to print to file."
        # print "I had "+str(self.chapter_count)+" chapters and "+str(self.route_count)+" routes"
        if self.title: outfile.write('% '+self.title+'\n')
        if self.author: outfile.write('% '+self.author+'\n')
        if self.date: outfile.write('% '+datetime.datetime.now().strftime('%A, %B %d, %I:%M:%S %p %z')+'\n')
        if self.introduction:
            outfile.write('\n\n')
            self.introduction.print_all_to_file(outfile, response)
        chapter_tracker=0
        for chapter in self.chapter_list:
            outfile.write('\n\n')
            chapter.print_all_to_file(outfile, response)
            chapter_tracker += 1
            # print str(chapter_tracker) + ' just printed chapter: '+chapter.title+'\n'
        if self.conclusion:
            outfile.write('\n\n')
            self.conclusion.print_all_to_file(outfile, response)


    def print_nav_to_file(self, parent_dir, response=True):
        nav_path = os.path.join(parent_dir, title2filename(self.title)+'.nav.dd')
        navfile = open(nav_path, 'w')
        if self.title: navfile.write('% '+self.title+'\n')
        if self.author: navfile.write('% '+self.author+'\n')
        if self.date: navfile.write('% '+datetime.datetime.now().strftime('%A, %B %d, %I:%M:%S %p %z')+'\n')
        if self.introduction:
            navfile.write('%# chapter/'+self.introduction.key_filepath+'.nav.dd\n')
            self.introduction.print_nav_to_file(parent_dir, response=response)
        for chapter in self.chapter_list:
            chapter.print_nav_to_file(parent_dir, response=response)
            navfile.write('%# chapter/'+chapter.key_filepath+'.nav.dd\n')
        if self.conclusion:
            self.conclusion.print_nav_to_file(parent_dir, response=response)
            navfile.write('%# chapter/'+self.conclusion.key_filepath+'.nav.dd\n')



    def print_status_report(self, status_file):
        for chapter in self.chapter_list:
            for route in chapter.route_list:
                stat_rep = route.get_status_report()
                if stat_rep is not None:
                    self.route_dict[route.title].add_status_stamp(**stat_rep)

        for route_title in self.route_dict:
            status = self.route_dict[route_title]
            ts = status.timestamp
            abbr_title_strt_ndx = route_title.find('/', 1)
            abbr_title = route_title[abbr_title_strt_ndx:]
            status_file.write(
                ts[8:10]+' '+ts[11:16]+' '+
                status.code.ljust(9)+' '+str(status.level)+' '+
                abbr_title+'\n'
            )

    def print_ch_status_report(self, ch_status_file):
        ch_status_file.write(self.title+'\n')
        if self.date:
            ch_status_file.write('% '+datetime.datetime.now().strftime('%A, %B %d, %I:%M:%S %p %z')+'\n\n')
        if self.introduction:
            self.introduction.print_to_ch_status_file(ch_status_file)

        for chapter in self.chapter_list:
            chapter.print_to_ch_status_file(ch_status_file)

        if self.conclusion:
            self.conclusion.print_to_ch_status_file(ch_status_file)

    def feed_line(self, line, from_filepath):
        line = line.rstrip()
        if line.startswith('% '):
            if not self.title:
                self.title = line[2:].strip()
                return
            elif not self.author:
                self.author = line[2:].strip()
                return
            elif not self.date:
                self.date = line[2:].strip()
                return
            else:
                pass # it will be picked up later as human text

        if line.startswith('# '):
            self.chapter_count += 1
            ch_title = line[2:].strip()
            if ch_title.upper().startswith('INTRODUCTION'):
                if not self.introduction:
                    self.current_chapter = ChapterDocUnit('Introduction', from_filepath)
                    self.introduction = self.current_chapter
                else:
                    raise Exception('Cannot have two INTRODUCTION chapters.')
            elif ch_title.upper().startswith('CONCLUSION'):
                if not self.conclusion:
                    self.current_chapter = ChapterDocUnit('Conclusion', from_filepath)
                    self.conclusion = self.current_chapter
                else:
                    raise Exception('Cannot have two CONCLUSION chapters')
            else:
                if not ch_title in self.chapter_set:
                    self.chapter_set.add(ch_title)
                    self.current_chapter = ChapterDocUnit(ch_title, from_filepath)
                    self.chapter_list.append(self.current_chapter)
                else:
                    raise Exception('Cannot have a duplicate chapter title: '+line)
        else:
            if line.startswith('## '):
                # self.route_count += 1
                route = line[3:].strip()
                self.route_dict[route] = StatusReport('BLANK', 6, datetime.datetime.now().isoformat())
            if self.current_chapter:
                self.current_chapter.feed_line(line, from_filepath)
            else: # we have no chapter yet
                if len(line) == 0:  # don't worry about blank lines before the first chapter
                    pass
                else:
                    raise Exception('No current chapter set when line received: '+line)


def title2filename(title):
    valid_chars = "-_.()%s%s" % (string.ascii_letters, string.digits)
    # print valid_chars
    filename_safe = title.replace('/', '1l')
    filename_safe = filename_safe.replace(' ', '_')
    # print filename_safe
    filename_safe = "".join(c for c in filename_safe if c in valid_chars).rstrip()
    # print filename_safe
    # print 'filename='+filename_safe.lower()
    return filename_safe.lower()


def initialize(doc_filepath, debug_output=None):
    print_feed=False
    line_feed=False
    file_feed=False
    if debug_output is None:
        pass
    elif debug_output == 'line_feed':
        line_feed=True
    elif debug_output == 'file_feed':
        file_feed=True
    elif debug_output == 'file_line_feed':
        print_feed=True
    else:
        print 'Unrecognized debug_output selection.'
        print 'Must be one of: "line_feed", "file_feed", or "file_line_feed"'
        print 'continuing with no debug_output'
        pass

    if print_feed:
        print '@@@@@@@@@@@@@@@@@@@@@@@@@ dd FEED @@@@@@@@@@@@@@@@@@@@@@@@@'
    global driven_doc
    driven_doc = DrivenDoc()
    root_dir, basename = os.path.split(doc_filepath)
    feed_file(driven_doc, doc_filepath, root_dir, line_feed, file_feed, print_feed, rcrsn_lvl=0)
    if print_feed:
        print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'


link_to_file_pattern = '(^%# (\w+.*)|^#### ((config|predict|response|runtime|status)/\w+.*))'
regex = re.compile(link_to_file_pattern)
def feed_file(driven_doc, filepath, root_dir, line_feed, file_feed, print_feed, rcrsn_lvl=0):
    full_filepath = os.path.join(root_dir, filepath)
    if file_feed:
        print 'docdriven: '+full_filepath
    filename = os.path.basename(full_filepath)
    from_filekey = filename[:filename.rfind('.')] # last index of .
    feeder_file = open(full_filepath, 'r')
    for line in feeder_file:
        match = regex.search(line)
        if match:
            # print match.groups()
            path = match.groups()[1] if match.groups()[1] and len(match.groups()[1]) > 0 else match.groups()[2]
            if print_feed:
                print ' '*(4*rcrsn_lvl)+'+---+ '+line,
            if not path.startswith(('config/', 'predict/', 'response/', 'runtime/', 'status/', 'chapter/')):
                raise Exception('cannot import from unrecognized location: '+path)
            if not path.endswith(('.json', '.py', '.dd')):
                raise Exception('cannot import unrecognized filetype: '+path)
            if not path.startswith('chapter/'):
                path = 'chapter/'+path
            include_filepath = os.path.join(root_dir, path)
            if match.groups()[3] is not None:
                feed_line(driven_doc, ('#### '+match.groups()[3]+'\n'), from_filekey, line_feed, print_feed, rcrsn_lvl+1)
                if match.groups()[3] == 'runtime':
                    feed_line(driven_doc, ('~'*42)+'  python\n', from_filekey, line_feed, print_feed, rcrsn_lvl+1)
                else:
                    feed_line(driven_doc, ('~'*44)+'  json\n', from_filekey, line_feed, print_feed, rcrsn_lvl+1)
                feed_file(driven_doc, include_filepath, root_dir, line_feed, file_feed, print_feed, rcrsn_lvl+1)
                feed_line(driven_doc, ('~'*50)+'\n', from_filekey, line_feed, print_feed, rcrsn_lvl+1)
            else:
                feed_file(driven_doc, include_filepath, root_dir, line_feed, file_feed, print_feed, rcrsn_lvl+1)
        else:
            feed_line(driven_doc, line, from_filekey, line_feed, print_feed, rcrsn_lvl)
    feeder_file.close()

def feed_line(driven_doc, line, from_filekey, line_feed, print_feed, rcrsn_lvl):
    if print_feed:
        print ' '*(4*rcrsn_lvl)+'| '+line
    if line_feed:
        print 'docdriven:    '+line.rstrip()
    driven_doc.feed_line(line, from_filekey)

def print_to_files(parent_dirpath, dd_all_response=True):
    print 'parent_dirpath='+str(parent_dirpath)
    global driven_doc
    filepath = os.path.join(parent_dirpath, title2filename(driven_doc.title))
    report_filepath = os.path.join(parent_dirpath, 'reports/')
    report_filepath = os.path.join(report_filepath, title2filename(driven_doc.title))

    dd_all_file = open(filepath+'.all.dd', 'w')
    driven_doc.print_all_to_file(dd_all_file, dd_all_response)
    dd_all_file.close()

    driven_doc.print_nav_to_file(parent_dirpath, response=dd_all_response)

    status_filepath = report_filepath+'.status'
    try:
        os.remove(status_filepath) # delete it if it already existed
    except:
       pass
    status_report = open(status_filepath, 'w').close()
    status_report = open(status_filepath, 'w')
    driven_doc.print_status_report(status_report)
    status_report.close()

    ch_status_filepath = status_filepath.replace('.status', '.ch.status')
    try:
        os.remove(ch_status_filepath) # delete it if it already existed
    except:
        pass
    ch_status_file = open(ch_status_filepath, 'w').close()
    ch_status_file = open(ch_status_filepath, 'w')
    driven_doc.print_ch_status_report(ch_status_file)
    ch_status_file.close()


def get_json_doc_structure():
    global driven_doc
    return driven_doc.get_json_doc_structure()

if __name__ == '__main__':
    routes_filepath = '/Users/Jon/dev/iit/nebula1/cwautopro/routes.dd'
    initialize(routes_filepath)
    print_to_file(routes_filepath)


