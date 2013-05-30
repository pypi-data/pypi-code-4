from config import get_config
from app import get_identity
import argparse

def main():
  parser = argparse.ArgumentParser(description='Get a FullContact report on somebody, and store it in Cloudant')
  parser.add_argument('email', type=str,
                     help='email of the person to report on')

  args = parser.parse_args()

  config = get_config('.fc_cli')
  profile = get_identity(config, email=args.email)
  return profile

if __name__ == '__main__':
  print main()