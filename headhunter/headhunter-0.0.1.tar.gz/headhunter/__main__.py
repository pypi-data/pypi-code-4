from runner import HunterRunner
import sys
import yaml
import os

try:
  sys.exit(HunterRunner(**yaml.load(open('/etc/headhunter.yaml'))).
    run(*sys.argv))
except KeyboardInterrupt:
  sys.exit(0)