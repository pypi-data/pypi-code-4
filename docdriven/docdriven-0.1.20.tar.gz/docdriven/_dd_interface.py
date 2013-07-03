import json
import logging
import datetime
import os
import pprint
from jsonschema import validate

from _dd_interface_util import title2filename

log = logging.getLogger(__name__)

# text sections
PRE_CONFIG = 0
CONFIG = 1
POST_CONFIG = 2
PREDICT = 3
POST_PREDICT = 4
RESPONSE = 5
POST_RESPONSE =6
RUNTIME = 7
POST_RUNTIME = 8
REPORT = 9
POST_REPORT = 10

# other sections
CHAPTER = 20


ch_count = 1
ch_route_count = 1


class DrivenDoc(object):
    def __init__(self, root_dir, filename):
        self.root_dir = root_dir
        self.filename = filename
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

    def print_all_to_file(self, outfile, response=True):
        if self.title: outfile.write('% '+self.title+'\n')
        if self.author: outfile.write('% '+self.author+'\n')
        if self.date: outfile.write('% '+datetime.datetime.now().strftime('%A, %B %d, %I:%M:%S %p %z')+'\n')
        if self.introduction:
            outfile.write('\n\n')
            self.introduction.print_all_to_file(outfile, response)
        for chapter in self.chapter_list:
            outfile.write('\n\n')
            chapter.print_all_to_file(outfile, response)
        if self.conclusion:
            outfile.write('\n\n')
            self.conclusion.print_all_to_file(outfile, response)

    def print_nav_to_file(self):
        nav_filename = os.path.join(self.root_dir, self.filename[:len(self.filename)-3]+'.nav.dd')
        nav_file = open(nav_filename, 'w')
        if self.title: nav_file.write('% '+self.title+'\n')
        if self.author: nav_file.write('% '+self.author+'\n')
        if self.date: nav_file.write('% '+datetime.datetime.now().strftime('%A, %B %d, %I:%M:%S %p %z')+'\n')
        if self.introduction:
            nav_file.write('%# chapter/'+self.introduction.key_filepath+'.nav.dd\n')
            self.introduction.print_nav_to_file()
        for chapter in self.chapter_list:
            chapter.print_nav_to_file()
            nav_file.write('%# chapter/'+chapter.key_filepath+'.nav.dd\n')
        if self.conclusion:
            self.conclusion.print_nav_to_file()
            nav_file.write('%# chapter/'+self.conclusion.key_filepath+'.nav.dd\n')

    def print_status_report(self, status_file):
        # accumulate all the status reports for each unique route in the
        # route_dict -- one route may have appeared in many chapters. The
        # add_status_stamp method is smart about how to accumlate status
        # stamps - basically, lowest status report prevails.
        for chapter in self.chapter_list:
            for route in chapter.route_list:
                stat_rep = route.get_status_report()
                if stat_rep is not None:
                    self.route_dict[route.title].add_status_stamp(**stat_rep)

        # then loop through all the unique routes and print them to the
        # status file.  The route_title is the same as the actual route
        # and it is the key in the route_dict - the value is the accumulated
        # status report for that route.
        for route_title in self.route_dict:
            report = self.route_dict[route_title]
            ts = report.timestamp
            # we lop off the first section just as a hack to save horizontal space
            # when printing -- it is redundant information, so we don't lose much
            abbr_title_strt_ndx = route_title.find('/', 1)
            abbr_title = route_title[abbr_title_strt_ndx:]
            # print the timestamp, then the status code, then the route
            status_file.write(
                ts[8:10]+' '+ts[11:16]+' '+
                report.code.ljust(9)+' '+str(report.level)+' '+
                abbr_title+'\n'
            )

    def print_ch_status_report(self, ch_status_file):
        ch_status_file.write(self.title+'\n')
        if self.date:
            ch_status_file.write(datetime.datetime.now().strftime('%A, %B %d, %I:%M:%S %p %z')+'\n\n')
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
                    self.current_chapter = ChapterDocUnit('Introduction', self.root_dir, from_filepath)
                    self.introduction = self.current_chapter
                else:
                    raise Exception('Cannot have two INTRODUCTION chapters.')
            elif ch_title.upper().startswith('CONCLUSION'):
                if not self.conclusion:
                    self.current_chapter = ChapterDocUnit('Conclusion', self.root_dir, from_filepath)
                    self.conclusion = self.current_chapter
                else:
                    raise Exception('Cannot have two CONCLUSION chapters')
            else:
                if not ch_title in self.chapter_set:
                    self.chapter_set.add(ch_title)
                    self.current_chapter = ChapterDocUnit(ch_title, self.root_dir, from_filepath)
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

    def get_json_section(self, section):
        if len(self.sections[section]) > 0:
            return json.loads(self.sections[section])
        else:
            return json.loads('{}')

    def put_json_section(self, section, jsonifiable_obj):
        if section in [1, 3, 5, 9]: # config, predict, response, report -- leaving out 7, runtime
            self.sections[section] = json.dumps(jsonifiable_obj, indent=4, separators=(',', ': '))
        else:
            raise Exception('cannot put json in section '+section)

    def get_keypath(self, section):
        if section == CHAPTER:
            if self.key_filepath is not None:
                return self.key_filepath
            else: # should never happen, since key_filepath should always be set
                return title2filename(self.title)
        elif section == CONFIG or section == PREDICT or section == RESPONSE or section == RUNTIME or section == REPORT:
            if len(self.section_keypaths[section])>0:
                return self.section_keypaths[section]
            else:
                if self.__class__.__name__ == 'ChapterDocUnit':
                    return self.key_filepath
                elif self.__class__.__name__ == 'RouteDocUnit':
                    return self.chapter.key_filepath+'.'+title2filename(self.title)
                else:
                    raise Exception('Unknown class type: '+self.__class__.__name__)

    def runtime_exec(self, config_predict_response_tuple_list):
        # print 'ADJUSTING FOR NEXT CONFIG - BEGIN'
        this_result = config_predict_response_tuple_list[-1][2]
        next_config = None
        next_predict = None
        exec self.sections[RUNTIME]
        # print 'ADJUSTING FOR NEXT CONFIG - FINISHED'
        return (next_config, next_predict)

    def report_stamp(self, code, level, timestamp, speed=0.0, note=None):
        isoformat = timestamp.isoformat()
        self.sections[REPORT] = json.dumps({
            'code':code,
            'level':level,
            'timestamp':isoformat[:10]+' '+isoformat[11:22],
            'speed':speed,
            'note':note
            }, indent=4, separators=(',',':'))

    def get_status_report(self):
        if len(self.sections[REPORT]) > 3:
            return json.loads(self.sections[REPORT])
        else:
            return None

    def write_nav_files(self, chapdir, chapter_file):
        index = PRE_CONFIG
        sects = ['human', 'config', 'human', 'predict', 'human', 'response', 'human', 'runtime', 'human', 'report', 'human']
        # log.debug('request to write_nav_files - chapdir: '+str(chapdir)+' - chapter_file: '+str(chapter_file))
        for section in self.sections:
            if index % 2 == 1: # if index to sections array is 1, 3, 5, 7, 9, 11, ... then we are dealing with code
                # log.debug(str(index)+' is odd, so its a code section')
                if len(self.sections[index]) > 0:
                    # log.debug('content found in section: '+str(index))
                    filepath = self.get_keypath(section=index)
                    # log.debug('found keypath: '+filepath)
                    if index == 7:
                        filepath += '.py'
                    else:
                        filepath += '.json'
                    chapter_file.write('#### '+sects[index]+'/'+filepath.rstrip()+'\n')
                    navdir = os.path.join(chapdir, sects[index])
                    # log.debug('navdir should be: '+navdir)
                    nav_filepath = os.path.join(navdir, filepath)
                    # log.debug('nav_filepath computed as: '+str(nav_filepath))
                    navfile = open(nav_filepath, 'w')
                    if index == 7:
                        navfile.write(self.sections[index]+'\n')
                    else:
                        navfile.write(self.pretty_json(self.sections[index])+'\n')
                    navfile.close()
                    # log.debug('closed '+str(nav_filepath))
                else:
                    # log.debug('no content, so writing header to chapter file...')
                    chapter_file.write('#### '+sects[index]+'/\n') # trailng slash indicates an empty code section
            else: # it is a text file meant for human, not machine consumption, so we write it to the chapter directly
                if len(self.sections[index].rstrip()) > 0:
                    chapter_file.write(self.sections[index].rstrip()+'\n')
            index += 1
            if self.__class__.__name__ == 'ChapterDocUnit' and index > 3:
                break # chapter doc units don't have response, runtime, or report - only routes do

    def as_string(self, response=True):
        doc_string = ''

        if len(self.sections[PRE_CONFIG]) > 0:
            doc_string += self.sections[PRE_CONFIG]

        if len(self.sections[CONFIG]) > 0:
            doc_string += '\n#### config\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[CONFIG])+'\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            # doc_string += '#### config/\n'
            pass

        if len(self.sections[POST_CONFIG]) > 0:
            doc_string += self.sections[POST_CONFIG]

        if len(self.sections[PREDICT]) > 0:
            doc_string += '\n#### predict\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[PREDICT])+'\n'
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            # doc_string += '#### predict/\n'
            pass

        if len(self.sections[POST_PREDICT]) > 0:
            doc_string += self.sections[POST_PREDICT]

        if len(self.sections[RESPONSE]) > 0 and response:
            doc_string += '\n#### response\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[RESPONSE])+'\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            # doc_string += '#### response/\n'
            pass

        if len(self.sections[POST_RESPONSE]) > 0:
            doc_string += self.sections[POST_RESPONSE]

        if len(self.sections[RUNTIME]) > 2:
            doc_string += '\n#### runtime\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  python\n'
            doc_string += self.sections[RUNTIME]+'\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            # doc_string += '#### runtime/\n'
            pass

        if len(self.sections[POST_RUNTIME])>0:
             doc_string += self.sections[POST_RUNTIME]

        if len(self.sections[REPORT]) > 0:
            doc_string += '\n#### report\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[REPORT])+'\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            # doc_string += '#### report/\n'
            pass

        if len(self.sections[POST_REPORT])>0:
            doc_string += self.sections[POST_REPORT]

        return doc_string

    def as_ch_report_string(self):
        titl = self.title
        if self.__class__.__name__ == 'RouteDocUnit':
            index = self.title[1:].find('/')
            if index > 0:
                titl = self.title[index+1:]
        if len(self.sections[REPORT]) < 1:
            return 'BLANK'.ljust(8)+' 6 '+titl
        else:
            report_stamp = json.loads(self.sections[REPORT])
            return report_stamp['code'].ljust(8)+' '+str(report_stamp['level'])+' '+titl

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
        if line.startswith(('# ','## ','% ', '!')):
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
                    # if self.code_index == PREDICT:
                        # try:
                        #     validate(self.sections[self.code_index], )
                        # except Exception, e:
                        #     print 'Invalid JSON schema in predict section for title: '+self.title
                        #     raise e

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
            if self.__class__.__name__ == 'ChapterDocUnit':
                raise Exception('A chapter cannot have a response -- only an incident can.')
            self.code_index = 5
            self.text_index = 6
            if header.endswith('response/'):
                self.CODE = False # empty code section just increments the text index counter
        elif header.startswith('runtime'):
            self.code_index = 7
            self.text_index = 8
            if header.endswith('runtime/'):
                self.CODE = False # empty code section just increments the text index counter
        elif header.startswith('report'):
            self.code_index = 9
            self.text_index = 10
            if header.endswith('report/'):
                self.CODE = False # empty code section just increments the text index counter
        else:
            raise Exception('invalid code header: '+header+' - must be one of: config, predict, response, report, or runtime')
        self.sections[self.code_index] = ''
        self.section_keypaths[self.code_index] = this_keypath

    def feed_line(self, line, from_filepath):
        self.consume_line(line, from_filepath)



class RouteDocUnit(AbstractDocUnit):
    def __init__(self, title, chapter):
        self.chapter = chapter
        super(RouteDocUnit, self).__init__(title, chapter.key_filepath)

    def print_all_to_file(self, outfile, response=True):
        global ch_count
        global ch_route_count
        outfile.write('\n## '+self.title+' {#ch-'+str(ch_count)+'-route-'+str(ch_route_count)+'}\n')
        ch_route_count += 1
        outfile.write(self.as_string(response))



class ChapterDocUnit(AbstractDocUnit):
    def __init__(self, title, doc_root_dir, key_filepath=None):
        self.doc_root_dir = doc_root_dir
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
        global ch_count
        global ch_route_count
        ch_route_count = 1
        outfile.write('# '+self.title+' {#ch-'+str(ch_count)+'}\n')
        outfile.write(self.as_string(response))
        for route in self.route_list:
            route.print_all_to_file(outfile, response)
        ch_count += 1

    def print_nav_to_file(self):
        chapter_dir = os.path.join(self.doc_root_dir, 'chapter/')
        chapter_filename = os.path.join(self.doc_root_dir, 'chapter/'+self.get_keypath(section=CHAPTER)+'.nav.dd')
        nav_chap_file = open(chapter_filename, 'w')
        nav_chap_file.write('# '+self.title+'\n')
        self.write_nav_files(chapter_dir, nav_chap_file)
        for route in self.route_list:
            nav_chap_file.write('## '+route.title+'\n')
            route.write_nav_files(chapter_dir, nav_chap_file)
        nav_chap_file.close()

    def accumulate_route_report(self):
        self.status_report = StatusReport()
        for route in self.route_list:
            self.status_report.accumulate_route_status(route.get_status_report())
        self.sections[REPORT] = json.dumps({
            'code':self.status_report.code,
            'level':self.status_report.level,
            'timestamp':self.status_report.timestamp,
            'speed':self.status_report.speed,
            'note':self.status_report.note
            }, indent=4, separators=(',',':'))

    def print_to_ch_status_file(self, ch_status_file):
        self.accumulate_route_report()
        ch_status_file.write(self.as_ch_report_string()+'\n')
        for route in self.route_list:
            ch_status_file.write('         '+route.as_ch_report_string()+'\n')
        ch_status_file.write('\n')


    def as_string(self, response=True):
        doc_string = ''

        if len(self.sections[PRE_CONFIG]) > 0:
            doc_string += self.sections[PRE_CONFIG]

        if len(self.sections[CONFIG]) > 0:
            doc_string += '\n#### config\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[CONFIG])+'\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            # doc_string += '#### config/\n'
            pass

        if len(self.sections[POST_CONFIG]) > 0:
            doc_string += self.sections[POST_CONFIG]

        if len(self.sections[PREDICT]) > 0:
            doc_string += '\n#### predict\n'
            doc_string += '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  json\n'
            doc_string += self.pretty_json(self.sections[PREDICT])+'\n'
            doc_string += '\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'
        else:
            # doc_string += '#### predict/\n'
            pass

        if len(self.sections[POST_PREDICT]) > 0:
            doc_string += self.sections[POST_PREDICT]

        return doc_string







