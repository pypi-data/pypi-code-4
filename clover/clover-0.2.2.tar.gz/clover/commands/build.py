import sys
import argparse

from clover.builder import Builder
from clover.command import Command
from clover.config.multiconfig import MultiDocConfig


argparser = argparse.ArgumentParser()
argparser.add_argument('config')
argparser.add_argument('id')


class Build(Command):
    def start(self, args):
        parsed_args = argparser.parse_args(args)
        mdc = MultiDocConfig(parsed_args.config)
        mdc.parse(open(parsed_args.config).read())
        config = mdc.get_config(parsed_args.id)

        output_file = config.read_option(config.options.output)

        # TODO: improve error logging
        
        builder = Builder(config)
        result = builder.build()
        # copy the results into the requested destinations

        with open(config.abspath(output_file), 'w') as f:
            f.write(result.wrap_source(config.read_option(config.options.output_wrapper)))

        sourcemap_output_file = config.read_option(config.options.output_sourcemap)

        if sourcemap_output_file:
            with open(config.abspath(sourcemap_output_file), 'w') as f:
                f.write(result.source_map)


if __name__ == '__main__':
    Build.run(sys.argv[1:])