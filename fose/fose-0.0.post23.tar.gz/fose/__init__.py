import sys, argparse
import pkg_resources
import fose.tests
import fose.compliance


def main():
    description='Core package of Framework for Open Science Evaluation.'
    parser = argparse.ArgumentParser(description)
    parser.add_argument('--test', action='store_true',help='Run unit tests.')
    parser.add_argument('--compliance', 
		help='Run compliance tests for the url COMPLIANCE.')
    args = parser.parse_args()
    if args.test:
        fose.tests.runall()
    if args.compliance:
		fose.compliance.run(args.compliance)

version = pkg_resources.get_distribution("fose").version
