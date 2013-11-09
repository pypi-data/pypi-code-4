#! /usr/bin/evn python
# -*- encoding: utf-8 -*-
"""
downyt - Youtube video downloader

Usage:
    downyt <videoid> [-t OUTPUT_TYPE] [-o OUTPUT_DIR] [-f]
    downyt pv <pyvideo_feed> [-t OUTPUT_TYPE] [-o OUTPUT_DIR] [-f]

Options:
    -o OUTPUT_DIR       Specify the output directory
    -t OUTPUT_TYPE      File type of the downloaded video (webm/mp4/3gp/flv)
    -f                  Overwrite existing files
"""
import os
import re
import sys
import math
import yaml
import six
import requests
import feedparser

from purl import URL
from docopt import docopt
from six.moves.urllib.parse import parse_qs


EXTENSION_TO_TYPE = {
    'webm': 'video/webm',
    'mp4': 'video/mp4',
    '3gp': 'video/3gpp',
    'flv': 'video/x-flv',
}


class DownytError(Exception):
    pass


class VideoInfo(object):
    request_url = 'http://www.youtube.com/get_video_info'

    def __init__(self, url_or_id):
        if URL(url_or_id).scheme():
            self.video_id = self.get_video_id_from_url(url_or_id)
        else:
            self.video_id = url_or_id
        params = {'video_id': self.video_id}
        response = requests.get(self.request_url, params=params)
        self.video_info = parse_qs(str(response.content))

    @property
    def title(self):
        try:
            title = self.video_info.get('title')[0]
        except (TypeError, IndexError):
            title = "You Tube Video {}".format(self.video_id)
        return title

    def get_filename(self, vformat='mp4'):
        fname, __ = re.subn('[^a-zA-Z0-9]', '_', self.title)
        return "{}.{}".format(fname, vformat)

    def get_video_id_from_url(self, video_url):
        video_url = URL(video_url)

        if 'youtube' not in video_url.host():
            raise DownytError(
                'Provided URL is not from YouTube: {}'.format(video_url)
            )

        return video_url.query_param('v')

    def get_video_url(self, vformat='mp4'):
        format_url_map = self.video_file_urls()

        format_url = format_url_map.get(EXTENSION_TO_TYPE.get(vformat.lower()))
        if not format_url:
            raise DownytError(
                "could not find matching URL for type '{}'".format(vformat)
            )
        return format_url

    def video_file_urls(self):
        """
        extract video file's url from VideoInfo object and return them
        """
        stream_map = self.video_info[
            u'url_encoded_fmt_stream_map'][0].split(',')
        format_url_map = {}
        for entry in [parse_qs(entry) for entry in stream_map]:
            entry_type = entry['type'][0]
            entry_type = entry_type.split(';')[0]

            url = "{}&signature={}".format(entry['url'][0], entry['sig'][0])
            format_url_map[entry_type] = url
        return format_url_map


def progress(fname, percent):
    marks = math.floor(40 * percent)
    fname = fname.rsplit('/', 1)[-1]
    pbar = '{fname:30} [{marks:40}]'.format(
        fname=fname[:30],
        marks=('#' * marks)
    )
    sys.stdout.write("{} {}%\r".format(pbar, int(percent * 100)))
    if percent >= 1:
        sys.stdout.write("\n")
        sys.stdout.flush()


def download(url, filename, force_overwrite=False):
    if os.path.exists(filename) and not force_overwrite:
        raise DownytError("File already exists, use '-f' to overwrite.")

    response = requests.get(url, stream=True)
    file_size = int(response.headers['content-length'])

    downloaded = 0
    with open(filename, 'wb') as fh:
        for chunk in response.iter_content(16384):
            fh.write(chunk)
            downloaded += len(chunk)
            progress(filename, (downloaded / file_size))


def _parse_feed(feed_url, output_dir, output_type):
    feed = feedparser.parse(feed_url)

    videos = []
    for entry in feed.entries:
        for link in entry.links:
            if not 'youtube' in link.href:
                continue

            video_info = VideoInfo(link.href, title=entry.title)
            videos.append((
                video_info.get_video_url(output_type),
                os.path.join(output_dir, video_info.get_filename(output_type)),
            ))
    return videos


def main():
    arguments = docopt(__doc__, version='downyt 0.1.0')

    output_type = arguments.get('-t') or 'mp4'
    output_dir = arguments.get('-o')

    if not output_dir:
        config_path = os.path.expanduser('~/.downyt/config.yml')
        if os.path.exists(config_path):
            with open(config_path) as cfg:
                config = yaml.safe_load(cfg)
        else:
            config = {}
        output_dir = config.get('output_dir') or os.getcwd()

    videos = []
    if arguments.get('pv'):
        videos.extend(
            _parse_feed(
                arguments.get('<pyvideo_feed>'),
                output_type=output_type,
                output_dir=output_dir,
            )
        )

    if arguments.get('<videoid>'):
        video_info = VideoInfo(arguments.get('<videoid>'))
        videos.append((
            video_info.get_video_url(vformat=output_type),
            os.path.join(
                output_dir,
                video_info.get_filename(vformat=output_type)
            ),
        ))

    for url, fname in videos:
        try:
            download(url, fname, force_overwrite=arguments.get('-f'))
        except DownytError as exc:
            six.print_(exc.args[0])
            return


if __name__ == '__main__':
    main()
