    #!/usr/bin/env python
    import argparse, sys
    def test_parse_args():
        my_argv = ["-f", "/home/fenton/project/setup.py"]
        setup = get_setup_file(my_argv)
        assert setup == "/home/fenton/project/setup.py"
    def get_setup_file(argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('-f')
        args = parser.parse_args(argv)
        return args.f
    if __name__ == '__main__':
        test_parse_args()
