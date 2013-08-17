import os
from StringIO import StringIO

import yaml
from parser import SettingsParser


# Ensure that argparse still works.
def test_normal_arg():
    parser = SettingsParser()
    parser.add_argument('--blah')

    args = parser.parse_args(['--blah', 'hello'])

    assert args.blah == 'hello'

def test_normal_default():
    parser = SettingsParser()
    parser.add_argument('--blah', default='nope')

    args = parser.parse_args([])

    assert args.blah == 'nope'


def test_env_var():
    os.environ['FAVCOLOR'] = 'blue'
    parser = SettingsParser()
    parser.add_argument('--color', env_var='FAVCOLOR')
    args = parser.parse_args([])
    assert args.color == 'blue'


def test_yaml_value():
    f = StringIO()
    f.write(yaml.safe_dump({'color': 'blue'}))
    f.seek(0)
    parser = SettingsParser(yaml_file=f)
    parser.add_argument('--color')
    args = parser.parse_args([])
    assert args.color == 'blue'


def test_env_var_default_used():
    parser = SettingsParser()
    parser.add_argument('--color', env_var='FAVCOLOR', default='green')

    # Make sure there's not actually a FAVCOLOR env var
    if 'FAVCOLOR' in os.environ:
        os.environ.pop('FAVCOLOR')

    args = parser.parse_args([])
    assert args.color == 'green'
