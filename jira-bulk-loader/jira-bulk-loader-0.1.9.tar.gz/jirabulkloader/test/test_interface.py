
import pytest
import jirabulkloader.interface as ji

def test_args_parse_without_config_file():
    assert vars(ji.get_options( ['-H', 'h1', '-U', 'u1', '-P', 'p1', 'f1'] )) == \
        { 
        'host' : 'h1', 
        'user' : 'u1', 
        'dry_run' : False, 
        'priority' : 'Medium', 
        'template_file' : 'f1',
        'duedate' : None,
        'password' : 'p1',
        'project' : None,
        }


