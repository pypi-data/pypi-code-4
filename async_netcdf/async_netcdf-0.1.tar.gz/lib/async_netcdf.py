import sys
import os
import shutil
import argparse 
import textwrap

class Open_With_Indent:
    """This class creates an open file were indentation is tracked"""

    def __init__(self,file_name,read_method):
        self.open = open(file_name,read_method)
        self._current_indent=0
    
    def writei(self,write_string):
        self.open.write(write_string.rjust(len(write_string)+self._current_indent))

    def inc_indent(self):
        self._current_indent+=3

    def dec_indent(self):
        if self._current_indent > 3:
            self._current_indent-=3
        else:
            self._current_indent=0

class Experiment_Setup:
    """ Sets an experiment for the CMIP5 archive """

    def __init__(self,options):
        for opt in dir(options):
            if opt[0] != '_' and opt not in ['ensure_value','read_file','read_module']:
                setattr(self,opt,getattr(options,opt))

        #For parallel option:
        self.parallel_dimension=None
        self.parallel_dimension_number=0

    def prepare_scripts(self):
        """ Prepares the scripts for bash launch """
        out=Open_With_Indent(self.compiled_bash_script,'w')

        #Define instructions:
        parallel_dimension=None
        instructions={
                      '#!PARALLEL' : start_parallel_instance,
                      '#!END PARA' : end_parallel_instance
                    }

        #Loop through lines:
        for line in self.bash_script:
                out.writei(line)
                for inst in instructions.keys():
                    if line.lstrip().upper()[:len(inst)]==inst:
                        self=instructions[inst](self,out,line)

        out.open.close()


def start_parallel_instance(self,out,line):
    #Keep track of the parallelized dimension. Cannot chunk it along different dimensions:
    if self.parallel_dimension != None:
        raise IOError('Attempting to parallelize a dimension without having closed the previous parallel instance')
    else:
        self.parallel_dimension = line.lstrip()[10:].rstrip('\n').strip()

    out.writei('#Creating a parallel loop over dimension '+self.parallel_dimension+' with '+str(self.num_procs)+' processors:\n')
    out.writei('#########################################################################\n')
    out.writei('#Identify the files to transfer\n')
    out.writei('GLOBIGNORE="${AN_ROOT_FILE}.'+self.parallel_dimension+'???.*"\n')
    out.writei('LIST_TEMP_FILE=$(ls ${AN_ROOT_FILE}*)\n')
    out.writei('GLOBIGNORE=""\n')
    out.writei('export LIST_FILE_ID=$(for FILE in ${LIST_TEMP_FILE}; do echo ${FILE#${AN_ROOT_FILE}}; done)\n')
    out.writei('export AN_ROOT_FILE="${AN_ROOT_FILE}"\n')

    out.writei('\n')
    out.writei('#Define splitting function:\n')
    out.writei('function parallel_dimension_'+self.parallel_dimension+str(self.parallel_dimension_number)+'() {\n')

    out.inc_indent()
    out.writei('cat > $1 <<\'EndOfFunction\'\n')
    out.writei('DIM_INDICES="$1"\n')
    out.writei('export AN_ROOT_FILE="${AN_ROOT_FILE}"\n')

    #FUNCTION TO CLEAN-UP
    out.writei('function async_clean(){\n')
    out.inc_indent()
    out.writei('NUM_ID=$1\n')
    out.writei('for FILE_ID in $LIST_FILE_ID; do\n')
    out.inc_indent()
    out.writei('rm ${AN_ROOT_FILE}.'+self.parallel_dimension+'${NUM_ID}${FILE_ID}\n')
    out.dec_indent()
    out.writei('done\n')
    out.writei('if [ -e "${AN_ROOT_FILE}" ]; then\n')
    out.inc_indent()
    out.writei('rm ${AN_ROOT_FILE}.'+self.parallel_dimension+'${NUM_ID}\n')
    out.dec_indent()
    out.writei('fi\n')
    out.dec_indent()
    out.writei('}\n')

    #FUNCTION TO PERFORM THE ASYNCHRONOUS COMPUTATION
    out.writei('function async_computation(){\n')
    out.inc_indent()
    out.writei('NUM_DIM=$1\n')
    out.writei('LAST_NUM=$2\n')
    out.writei('NUM_ID=$3\n')
    out.writei('for FILE_ID in $LIST_FILE_ID; do\n')
    out.inc_indent()
    out.writei('DIM_LENGTH=`ncks -H -v '+self.parallel_dimension+' ${AN_ROOT_FILE}${FILE_ID} | wc -l`\n')
    out.writei('let "DIM_LENGTH-=1"\n')
    out.writei('if [ "$DIM_LENGTH" -gt "1" ]; then\n')
    out.inc_indent()
    out.writei('ncks -d '+self.parallel_dimension+',${NUM_DIM},${LAST_NUM} ${AN_ROOT_FILE}${FILE_ID} ${AN_ROOT_FILE}.'+self.parallel_dimension+'${NUM_ID}${FILE_ID}\n')
    out.dec_indent()
    out.writei('else\n')
    out.inc_indent()
    out.writei('cp ${AN_ROOT_FILE}${FILE_ID} ${AN_ROOT_FILE}.'+self.parallel_dimension+'${NUM_ID}${FILE_ID}\n')
    out.dec_indent()
    out.writei('fi\n')
    out.dec_indent()
    out.writei('done\n')

    out.writei('if [ -e "${AN_ROOT_FILE}" ]; then\n')
    out.inc_indent()
    out.writei('ncks -d '+self.parallel_dimension+',${NUM_DIM},${LAST_NUM} ${AN_ROOT_FILE} ${AN_ROOT_FILE}.'+self.parallel_dimension+'${NUM_ID}\n')
    out.dec_indent()
    out.writei('fi\n')
    out.writei('export AN_ROOT_FILE="${AN_ROOT_FILE}.'+self.parallel_dimension+'${NUM_ID}"\n')
    out.writei('#########################################################################\n')
    out.inc_indent()
    out.inc_indent()
    return self

def end_parallel_instance(self,out,line):
    if line.lstrip()[14:].rstrip('\n').strip() != self.parallel_dimension:
        raise IOError('Attempting to close parallel instance {0} when parallel instance {1} is open'.format(line.lstrip()[14:].rstrip('\n').strip(),self.parallel_dimension) )
    else:
        out.dec_indent()
        out.dec_indent()
        out.writei('}\n')
        out.dec_indent()
        out.writei('NUM_DIM=$(echo $DIM_INDICES | tr \',\' \' \' | awk -F\' \' \'{ print $1 }\')\n')
        out.writei('LAST_NUM=$(echo $DIM_INDICES | tr \',\' \' \' | awk -F\' \' \'{ print $2 }\')\n')
        out.writei('NUM_ID=$(printf "%03d" ${NUM_DIM})\n')
        out.writei('async_computation $NUM_DIM $LAST_NUM $NUM_ID')
        out.writei('#########################################################################\n')
        out.writei('for FILE_ID in $LIST_FILE_ID; do rm -f ${AN_ROOT_FILE}${FILE_ID}; done\n')
        out.writei('if [ -e "${AN_ROOT_FILE}" ]; then\n')
        out.writei('rm ${AN_ROOT_FILE}\n')
        out.writei('fi\n')
        out.writei('\n')
        if self.parallel_dimension != 'time':
            out.writei('LIST_LOCAL_FILE=`ls ${AN_ROOT_FILE}*`\n')
            out.writei('export LIST_LOCAL_FILE_ID=`for FILE in ${LIST_LOCAL_FILE}; do echo ${FILE#${AN_ROOT_FILE}}; done`\n')
            out.writei('for FILE_ID in $LIST_LOCAL_FILE_ID; do\n')
            out.inc_indent()
            out.writei('ncpdq -a '+self.parallel_dimension+',time ${AN_ROOT_FILE}${FILE_ID} ${AN_ROOT_FILE}${FILE_ID}_perm\n')
            out.writei('mv ${AN_ROOT_FILE}${FILE_ID}_perm ${AN_ROOT_FILE}${FILE_ID}\n')
            out.dec_indent()
            out.writei('done\n')
        out.dec_indent()
        out.open.write('EndOfFunction\n')
        out.dec_indent()
        out.writei('}\n')
        out.writei('parallel_dimension_'+self.parallel_dimension+str(self.parallel_dimension_number)+' ${AN_ROOT_FILE}.'+self.parallel_dimension+'_function'+str(self.parallel_dimension_number)+'.sh\n')
        out.writei('#Performing parallel computation\n')
        out.writei('DIM_LENGTHS=`for FILE in $LIST_TEMP_FILE; do ncks -H -v '+self.parallel_dimension+' ${FILE} | wc -l; done`\n')
        out.writei('DIM_LENGTH=`for DIM in ${DIM_LENGTHS}; do echo $DIM; done | awk \'{if(min==""){min=max=$1}; if($1>max) {max=$1}; if($1<min) {min=$1}} END {print max}\'`\n')
        out.writei('let "DIM_LENGTH -= 2"\n')
        if line.lstrip()[:14].upper() == '#!END PARAFULL' or self.debug:
            out.writei('STRIDE=1\n')
        else:
            out.writei('STRIDE=`expr $DIM_LENGTH / '+str(self.num_procs)+' + 1`\n')
        out.writei('NUM_DIM=0\n')
        out.writei('while [ "$NUM_DIM" -le "$DIM_LENGTH" ]; do if [ "$((${NUM_DIM} + ${STRIDE} - 1))" -ge "$DIM_LENGTH" ]; then \\\n')
        out.writei('echo ${NUM_DIM},${DIM_LENGTH}; else echo ${NUM_DIM},$((${NUM_DIM} + ${STRIDE} - 1)); fi; \\\n')
        out.writei('let "NUM_DIM += ${STRIDE}"; done |\\\n')
        if self.debug:
            out.writei('parallel --tty "bash ${AN_ROOT_FILE}.'+self.parallel_dimension+'_function'+str(self.parallel_dimension_number)+'.sh {}"\n')
        else:
            out.writei('parallel -j'+str(self.num_procs)+' -k "bash ${AN_ROOT_FILE}.'+self.parallel_dimension+'_function'+str(self.parallel_dimension_number)+'.sh {}"\n')
        out.writei('rm ${AN_ROOT_FILE}.'+self.parallel_dimension+'_function'+str(self.parallel_dimension_number)+'.sh\n')
        out.writei('\n')
        out.writei('#Delete files that were deleted in the parallel process\n')
        out.writei('for FILE_ID in $LIST_FILE_ID; do\n')
        out.inc_indent()
        out.writei('if [ ! -f ${AN_ROOT_FILE}.'+self.parallel_dimension+'000${FILE_ID} ]; then rm ${AN_ROOT_FILE}${FILE_ID}; fi\n')
        out.dec_indent()
        out.writei('done\n')

        out.writei('#Recombine output files\n')
        out.writei('LIST_PARALLEL_FILE=`ls ${AN_ROOT_FILE}.'+self.parallel_dimension+'000*`\n')
        out.writei('LIST_PARALLEL_FILE_ID=`for FILE in ${LIST_PARALLEL_FILE}; do echo ${FILE#${AN_ROOT_FILE}.'+self.parallel_dimension+'000}; done`\n')

        out.writei('for FILE_ID in $LIST_PARALLEL_FILE_ID; do\n')
        out.inc_indent()
        out.writei('if [ ! -f ${AN_ROOT_FILE}${FILE_ID} ]; then\n')
        out.inc_indent()
        out.writei('ncrcat -h ${AN_ROOT_FILE}.'+self.parallel_dimension+'???${FILE_ID} ${AN_ROOT_FILE}${FILE_ID}\n')
        out.writei('rm ${AN_ROOT_FILE}.'+self.parallel_dimension+'???${FILE_ID}\n')
        if self.parallel_dimension != 'time':
            out.writei('ncpdq -h -a time,'+self.parallel_dimension+' ${AN_ROOT_FILE}${FILE_ID} ${AN_ROOT_FILE}${FILE_ID}_perm\n')
            out.writei('mv ${AN_ROOT_FILE}${FILE_ID}_perm ${AN_ROOT_FILE}${FILE_ID}\n')
        out.dec_indent()
        out.writei('else\n')
        out.inc_indent()
        out.writei('rm ${AN_ROOT_FILE}.'+self.parallel_dimension+'???${FILE_ID}\n')
        out.dec_indent()
        out.writei('fi\n')
        out.dec_indent()
        out.writei('done\n')
        out.writei('#########################################################################\n')

        #These parameters are important if many parallel instances are specified:
        self.parallel_dimension=None
        self.parallel_dimension_number+=1
    return self

def main():

    #Option parser
    description=textwrap.dedent('''\
    This script compiles a BASH script for simple parallelization
    
    Created scripts might require:
    NCO 4.0.8 w/ netCDF4/HDF5
    timeout
    gnu-parallel
    ''')
    epilog="Frederic Laliberte, Paul J. Kushner, University of Toronto, 12/2012"
    usage = "%(prog)s [options] bash_script compiled_bash_script"
    version_num='0.2'
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                            description=description,
                            usage=usage,
                            version='%(prog)s '+version_num,
                            epilog=epilog)
    parser.add_argument('bash_script',
                                 type=argparse.FileType('r'),
                                 help='Bash script to \'compile\' (input)')
    parser.add_argument('compiled_bash_script',
                                 help='Compiled bash script (output)')

    #Setup options
    setup_group=parser.add_argument_group("Setup","These options must be set when using this script")
    setup_group.add_argument("--debug",dest="debug",
                      default=False, action="store_true",
                      help="Debug flag.")
    setup_group.add_argument("--num_procs","-j",dest="num_procs",
                      default=1,
                      help="Launches the scripts.")

    #Processing Options
    proc_group=parser.add_argument_group("Processing",
                            "Use these options to set parallelized options.\n\
                             BEWARE! Asynchronous options are largely untested!")
    proc_group.add_argument("-t","--timeout",dest="timeout",
                      default="1h",
                      help="Timeout a process after that amount of time.")

    options = parser.parse_args()

    experiment = Experiment_Setup(options)
    experiment.prepare_scripts()

if __name__ == "__main__":
    main()
