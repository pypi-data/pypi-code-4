
import pytest

def test_links_between_h4_and_h5_tasks( te, std_te_tasks, dry_run_key ):
    from mock import MagicMock, call
    te.create_link = MagicMock()
    te.create_tasks( std_te_tasks )
    assert te.create_link.call_args_list == [call(dry_run_key, dry_run_key), call(dry_run_key, dry_run_key)]

