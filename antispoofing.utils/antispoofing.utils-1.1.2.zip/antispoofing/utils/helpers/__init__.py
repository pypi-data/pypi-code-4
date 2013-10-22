from .score_reader import *
import os


def write_icb2013_score(scores_list, output_dir):
  """
  Write the files for the ICB 2013 competition

  Keyword parameters:

    scores_list
      List of scores. The format of the list is

      [
        [file_name, 1.0],
        [file_name, -1.0]
        .
        .
        .
        [file_name, 0.0]
      ]

   output_dir
     Output directory
  """
  import os
  
  def write_txt(path,list):
    f     = open(path,'w')
    for l in list:
      f.write(l[0] + " " + str(l[1]) + "\n")
    f.close()
	
  train_list     = [s for s in scores_list if(s[0][0:5]=='train')]
  devel_list     = [s for s in scores_list if(s[0][0:5]=='devel')]
  anonymous_list = [s for s in scores_list if(s[0][0:5]=='anony')]

  write_txt(os.path.join(output_dir,'train.txt'),train_list)
  write_txt(os.path.join(output_dir,'devel.txt'),devel_list)
  write_txt(os.path.join(output_dir,'anonymous.txt'),anonymous_list)


def ensure_dir(dirname):
  """ Creates the directory dirname if it does not already exist,
      taking into account concurrent 'creation' on the grid.
      An exception is thrown if a file (rather than a directory) already 
      exists. """
  try:
    # Tries to create the directory
    os.makedirs(dirname)
  except OSError:
    # Check that the directory exists
    if os.path.isdir(dirname): pass
    else: raise
