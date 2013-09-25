from StringIO import StringIO
import argparse
import json
import os
import subprocess
import sys
import tempfile

import pandas as pd


# aesthetic fields
AES_FIELDS = [
  'x',
  'y',
  'ymin',
  'ymax',
  'color',
  'fill',
  'alpha',
  'group',
  'size',
  'shape',
  'linetype',
  'weight',
]

# template for R script
TEMPLATE = """
library(ggplot2)

# read data in
data <- read.csv("{data}", header = T)

# convert date columns to date objects
for (i in names(data)) {{
  try({{
    data[i] <- as.Date(data[[i]])
  }})
}}

# plot it all
p <- ggplot(data, aes({aes_args})) {geom} {facet} {etc}
ggsave(filename = "{output}", plot = p)
"""

GEOM_TEMPLATE = """+ geom_{name}({geom_args})"""

FACET_TEMPLATE = """+ facet_grid({facet_args}, scales = \"{scales}\")"""

ETC_TEMPLATE = """+ {etc}"""

def plot(args):
    # read data from JSON

    if args.intype == 'json':
      df = pd.DataFrame.from_records(json.load(args.infile))
    elif args.intype == 'csv':
      df = pd.read_csv(args.infile)
    else:
      raise Exception("Unsupported input type: {}".format(args.intype))

    # construct geom string
    aes_args  = []
    geom_args = []
    for prop in AES_FIELDS:
      if getattr(args, prop) is not None:
        value = getattr(args, prop)

        if value not in df.columns:
          if value.startswith("..") and value.endswith(".."):
            # this is just a function of the data, that's OK
            aes_args.append("{} = {}".format(prop, value))
          elif value.startswith("I(") and value.endswith(")"):
            # You can't put I(...) in the aesthetic; put it as a literal
            # argument to the geom instead
            geom_args.append("{} = {}".format(prop, value))
          else:
            # I don't know how to interpret this value
            raise Exception((
              "You chose to set {col} = {val}, "
              "but the column doesn't exist in the"
              " data."
            ).format(col=prop, val=value))
        else:
          # append one more arg to the aesthetic
          aes_args.append("{} = {}".format(prop, value))


    # construct aes arg string
    aes_args = ", ".join(aes_args)

    # construct geom arg string
    if args.geom is not None:
      geom = GEOM_TEMPLATE.format(
        name      = args.geom,
        geom_args = ", ".join(geom_args),
      )
    else:
      geom = ""

    # construct facet string
    if args.facet is not None:
      if not '~' in args.facet:
        facet_args = ". ~ " + args.facet
      else:
        facet_args = args.facet

      facet = FACET_TEMPLATE.format(
        facet_args = facet_args,
        scales     = args.facet_scale
      )
    else:
      facet = ""

    # construct etc string
    if args.etc is not None:
      etc = ETC_TEMPLATE.format(etc=args.etc)
    else:
      etc = ""

    if not etc and not geom:
      raise Exception("You need to specify 'geom' or 'etc' or there's nothing to plot!")

    # write data to disk
    with tempfile.NamedTemporaryFile('w+') as tmp:
      df.to_csv(tmp, encoding="utf-8", index=False)
      tmp.flush()

      # generate R code for plotting
      script = TEMPLATE.format(
        data        = tmp.name,
        aes_args    = aes_args,
        geom        = geom,
        facet       = facet,
        etc         = etc,
        output      = args.outfile
      )

      # run R
      command = "R --vanilla <<< '{script}'".format(script=script)
      proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

      # make sure it completed successfully
      proc.wait()
      if proc.returncode != 0:
        sys.stderr.write(script + "\n")
        sys.stderr.write(proc.stderr.read() + "\n")
        raise Exception("R returned status code: {}".format(proc.returncode))

      # "open" is only available on OSX
      if sys.platform == 'darwin':
        subprocess.call(["open", args.outfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # print stuff to stdout
    print js


def check():
  if subprocess.call("R --version", shell=True,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE) != 0:
    raise Exception("Unable to run R. Did you install it?")
  if not subprocess.call("R --vanilla <<< 'library(ggplot2)'", shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE) == 0:
    raise Exception("ggplot2 isn't installed! Run 'install.packages(ggplot2)' in R first.")


def main():
  # make sure R dependencies are available
  check()

  # command line arg parsing
  parser = argparse.ArgumentParser("ggplot from the command line!")

  for prop in AES_FIELDS:
    parser.add_argument("--{}".format(prop))
  parser.add_argument('--facet',
      help="facet string; e.g. 'col1 ~ col2' or just 'col1'")
  parser.add_argument('--facet-scale',
      choices=['free', 'fixed'],
      default="free",
      help="link each subplot's axis together?")
  parser.add_argument('--geom',
      help="geometry (type of graph)")
  parser.add_argument('--etc',
      help="Additional R code to append to the plot")
  parser.add_argument( '--infile',
      type=argparse.FileType('r'),
      default=sys.stdin,
      help="input source file (defaults to stdin)")
  parser.add_argument( '--intype',
      choices=['json', 'csv'],
      default="json",
      help='input format (json: array of json objects; csv: comma separated file)')
  parser.add_argument( '--outfile',
      default="Rplots.png",
      help="where to save the figure (defaults to Rplots.png)")

  args = parser.parse_args()

  plot(args)


if __name__ == '__main__':
  main()
