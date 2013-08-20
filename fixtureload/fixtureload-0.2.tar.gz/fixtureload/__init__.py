import json
import os

__author__ = 'ozanturksever'

fixture_source_dir = '.'


def set_source_dir(dir_path):
    global fixture_source_dir
    fixture_source_dir = dir_path


def load(fixture_path):
    path = parse_fixture_path(fixture_path)
    with open(os.path.join(fixture_source_dir, path['source_file'])) as source:
        fixtures = json.loads(source.read())
        return fixtures.get(path['fixture_desc'], {}).get('samples', {}).get(path['fixture'])


def parse_fixture_path(fixture_path):
    parts = fixture_path.split('/')
    if len(parts) != 3:
        raise ValueError('Fixture Path is not valid (%s)' % fixture_path)
    return {
        'source_file': parts[0] + '.json',
        'fixture_desc': parts[1],
        'fixture': parts[2]
    }