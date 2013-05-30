from config import get_config
from app import get_identity
import argparse

parser = argparse.ArgumentParser(description='Get a FullContact report on somebody, and store it in Cloudant')
parser.add_argument('email', type=str,
                   help='email of the person to report on')

args = parser.parse_args()

if __name__ == '__main__':
  config = get_config('.fc_cli')
  status, profile = get_identity(config, email=args.email)
