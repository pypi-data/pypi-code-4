
import pytest
import os
import sys
import shutil
import textwrap

from tempfile import  mkdtemp
tmp_dir = mkdtemp(prefix='rmoldkern_tmp')
shutil.copy('rmoldkernels', os.path.join(tmp_dir, 'rmoldkernels.py'))
sys.path.insert(0, tmp_dir)
import rmoldkernels
sys.path.pop(0)
shutil.rmtree(tmp_dir)

class TestStrToTuple:
    def test_empty(self):
        assert rmoldkernels.str_to_tuple('') == ()

    def test_non_num(self):
        assert rmoldkernels.str_to_tuple('abcd') == ()

    def test_non_single_num(self):
        # leading and trailing non-numbers are skipped
        assert rmoldkernels.str_to_tuple('ab9cd') == (9,)

    def test_multi_num_multi_divider(self):
        assert rmoldkernels.str_to_tuple('ab1cd2ef3ghi') == (1,2,3)

    def test_multi_num_single_divider(self):
        assert rmoldkernels.str_to_tuple('1-2.3') == (1,2,3)

@pytest.fixture
def rok():
    return rmoldkernels.RemoveOldKernels()

class TestRmOldKernels:
    ll = textwrap.dedent("""\
    un  linux-headers-3.2.0-32         ...
    un  linux-headers-3.2.0-32-generic ...
    un  linux-image-3.2.0-32-generic   ...
    ii  linux-headers-3.2.0-53         ...
    ii  linux-headers-3.2.0-53-generic ...
    ii  linux-image-3.2.0-53-generic   ...
    ii  linux-headers-3.2.0-54         ...
    ii  linux-headers-3.2.0-54-generic ...
    ii  linux-image-3.2.0-54-generic   ...
    ii  linux-headers-3.2.0-55         ...
    ii  linux-headers-3.2.0-55-generic ...
    ii  linux-image-3.2.0-55-generic   ...
    ii  linux-headers-3.2.0-56         ...
    ii  linux-headers-3.2.0-56-generic ...
    ii  linux-image-3.2.0-56-generic   ...
    ii  linux-headers-generic          ...
    ii  linux-kernel-headers           ...
    """)

    def test_empty(self, rok):
        with pytest.raises(rmoldkernels.NoKernelInstalledError):
            rok.gen_list_map("", (3,2,0,55))

    def test_only_active(self, rok):
        assert rok.gen_list_map(textwrap.dedent("""\
        ii  linux-headers-3.2.0-55         ...
        ii  linux-headers-3.2.0-55-generic ...
        ii  linux-image-3.2.0-55-generic   ...
        ii  linux-headers-generic          ...
        """), (3,2,0,55))[0] == []

    def test_active_not_in_list(self, rok):
        with pytest.raises(rmoldkernels.ActiveNotInstalledError):
            rok.gen_list_map(textwrap.dedent("""\
            ii  linux-headers-3.2.0-55         ...
            ii  linux-headers-3.2.0-55-generic ...
            ii  linux-image-3.2.0-55-generic   ...
            ii  linux-headers-generic          ...
            """), (3,2,0,48))[0] == []

    def test_active_not_last_installed(self, rok):
        assert rok.gen_list_map(textwrap.dedent("""\
        ii  linux-headers-3.2.0-55         ...
        ii  linux-headers-3.2.0-55-generic ...
        ii  linux-image-3.2.0-55-generic   ...
        ii  linux-headers-3.2.0-56         ...
        ii  linux-headers-3.2.0-56-generic ...
        ii  linux-image-3.2.0-56-generic   ...
        ii  linux-headers-generic          ...
        ii  linux-kernel-headers           ...
        """), (3,2,0,55))[0] == []

    def test_bogus_dpkg_match(self, rok):
        assert rok.gen_list_map(textwrap.dedent("""\
        ii  heffalump-pooh         ...
        ii  linux-headers-3.2.0-55-generic ...
        ii  linux-image-3.2.0-55-generic   ...
        ii  linux-headers-3.2.0-56         ...
        ii  linux-headers-3.2.0-56-generic ...
        ii  linux-image-3.2.0-56-generic   ...
        ii  linux-headers-generic          ...
        ii  linux-kernel-headers           ...
        """), (3,2,0,56))[0] == [(3,2,0,55)]

    # test on a more realistic list

    def test_list_active_last(self, rok):
        res = rok.gen_list_map(self.ll, (3,2,0,56))
        assert res[0] == [(3,2,0,53), (3,2,0,54), (3,2,0,55)]
        assert rok.gather_packages(res[0], res[1]) == [
            "linux-headers-3.2.0-53",
            "linux-headers-3.2.0-53-generic",
            "linux-image-3.2.0-53-generic",
            "linux-headers-3.2.0-54",
            "linux-headers-3.2.0-54-generic",
            "linux-image-3.2.0-54-generic",
            "linux-headers-3.2.0-55",
            "linux-headers-3.2.0-55-generic",
            "linux-image-3.2.0-55-generic",
        ]

    def test_list_active_first(self, rok):
        assert rok.gen_list_map(self.ll, (3,2,0,53))[0] == \
               [(3,2,0,54), (3,2,0,55)]

    def test_list_active_middle(self, rok):
        assert rok.gen_list_map(self.ll, (3,2,0,54))[0] == \
               [(3,2,0,53), (3,2,0,55)]

    def test_active_last_installed(self, rok):
        assert rok.gen_list_map(self.ll, (3,2,0,56))[0] == \
               [(3,2,0,53), (3,2,0,54), (3,2,0,55)]

    def test_list_active_extra_keep_active_last(self, rok):
        assert rok.gen_list_map(self.ll, (3,2,0,56), extra_keep=1)[0] == \
               [(3,2,0,53), (3,2,0,54)]

    def test_list_active_extra_keep2_active_last(self, rok):
        assert rok.gen_list_map(self.ll, (3,2,0,56), extra_keep=2)[0] == \
               [(3,2,0,53)]

    def test_list_active_extra_keep_active_not_last(self, rok):
        assert rok.gen_list_map(self.ll, (3,2,0,54), extra_keep=1)[0] == \
               [(3,2,0,53), (3,2,0,55)]

    def test_list_active_extra_keep2_active_not_last(self, rok):
        assert rok.gen_list_map(self.ll, (3,2,0,54), extra_keep=2)[0] == \
               [(3,2,0,53)]

