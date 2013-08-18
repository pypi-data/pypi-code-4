#!/usr/bin/python
import re, datetime

def to_timedelta(timecode):
    r = re.search('(\d{2}):(\d{2}):(\d{2}),(\d{3})', timecode)
    h, m, s, ms = tuple([int(value) for value in list(r.groups())])
    return datetime.timedelta(seconds=s + m * 60 + h * 60 * 60, microseconds=ms * 1000)

def to_timecode(timedelta):
    ms = timedelta.seconds * 1000 + timedelta.microseconds / 1000
    hours, remainder = divmod(ms, 3600000)
    minutes, remainder = divmod(remainder, 60000)
    seconds, milliseconds = divmod(remainder, 1000)
    return '%0.2d:%0.2d:%0.2d,%0.3d' % (hours, minutes, seconds, milliseconds)

def adjust_srt(source_file, target_file, offset_ms):
    adjusted = lambda t: to_timecode(to_timedelta(t) + datetime.timedelta(microseconds=offset_ms * 1000))
    for line in source_file:
        r = re.search('(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', line)
        if r:
            line = '%s --> %s\n' % (adjusted(r.group(1)), adjusted(r.group(2)))
        target_file.write(line)

if __name__ == '__main__':
    import sys, argparse

    parser = argparse.ArgumentParser(description='Adjust timecodes in srt file.')
    parser.add_argument('source', help='Source file name')
    parser.add_argument('offset', type=int, help='Offset in milliseconds')
    parser.add_argument('-o', '--output', help='Output file name')
    args = parser.parse_args()

    source_file = open(args.source)
    if args.output:
        target_file = open(args.output, 'w')
    else:
        target_file = sys.stdout

    adjust_srt(source_file, target_file, args.offset)
