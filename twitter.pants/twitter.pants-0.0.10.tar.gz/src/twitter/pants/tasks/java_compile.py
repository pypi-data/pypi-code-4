# ==================================================================================================
# Copyright 2011 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

from collections import defaultdict

import os
import shlex

from twitter.common.dirutil import safe_open, safe_mkdir

from twitter.pants import has_sources, is_apt
from twitter.pants.tasks import TaskError
from twitter.pants.tasks.jvm_compiler_dependencies import Dependencies
from twitter.pants.tasks.nailgun_task import NailgunTask


# Well known metadata file to auto-register annotation processors with a java 1.6+ compiler
_PROCESSOR_INFO_FILE = 'META-INF/services/javax.annotation.processing.Processor'


_JMAKE_MAIN = 'com.sun.tools.jmake.Main'


# From http://kenai.com/projects/jmake/sources/mercurial/content/src/com/sun/tools/jmake/Main.java?rev=26
# Main.mainExternal docs.
_JMAKE_ERROR_CODES = {
   -1: 'invalid command line option detected',
   -2: 'error reading command file',
   -3: 'project database corrupted',
   -4: 'error initializing or calling the compiler',
   -5: 'compilation error',
   -6: 'error parsing a class file',
   -7: 'file not found',
   -8: 'I/O exception',
   -9: 'internal jmake exception',
  -10: 'deduced and actual class name mismatch',
  -11: 'invalid source file extension',
  -12: 'a class in a JAR is found dependent on a class with the .java source',
  -13: 'more than one entry for the same class is found in the project',
  -20: 'internal Java error (caused by java.lang.InternalError)',
  -30: 'internal Java error (caused by java.lang.RuntimeException).'
}
# When executed via a subprocess return codes will be treated as unsigned
_JMAKE_ERROR_CODES.update((256+code, msg) for code, msg in _JMAKE_ERROR_CODES.items())


def _is_java(target):
  return has_sources(target, '.java')


class JavaCompile(NailgunTask):
  @classmethod
  def setup_parser(cls, option_group, args, mkflag):
    NailgunTask.setup_parser(option_group, args, mkflag)

    option_group.add_option(mkflag("warnings"), mkflag("warnings", negate=True),
                            dest="java_compile_warnings", default=True,
                            action="callback", callback=mkflag.set_bool,
                            help="[%default] Compile java code with all configured warnings "
                                 "enabled.")

    option_group.add_option(mkflag("args"), dest="java_compile_args", action="append",
                            help = "Pass these extra args to javac.")

  def __init__(self, context):
    NailgunTask.__init__(self, context, workdir=context.config.get('java-compile', 'nailgun_dir'))

    workdir = context.config.get('java-compile', 'workdir')
    self._classes_dir = os.path.join(workdir, 'classes')
    self._resources_dir = os.path.join(workdir, 'resources')
    self._dependencies_file = os.path.join(workdir, 'dependencies')

    self._jmake_profile = context.config.get('java-compile', 'jmake-profile')
    self._compiler_profile = context.config.get('java-compile', 'compiler-profile')

    self._opts = context.config.getlist('java-compile', 'args')
    self._jvm_args = context.config.getlist('java-compile', 'jvm_args')

    self._javac_opts = []
    if context.options.java_compile_args:
      for arg in context.options.java_compile_args:
        self._javac_opts.extend(shlex.split(arg))
    else:
      self._javac_opts.extend(context.config.getlist('java-compile', 'javac_args', default=[]))

    if context.options.java_compile_warnings:
      self._opts.extend(context.config.getlist('java-compile', 'warning_args'))
    else:
      self._opts.extend(context.config.getlist('java-compile', 'no_warning_args'))

    self._confs = context.config.getlist('java-compile', 'confs')

  def execute(self, targets):
    java_targets = filter(_is_java, targets)
    if java_targets:
      jmake_classpath = self.profile_classpath(self._jmake_profile)
      compiler_classpath = self.profile_classpath(self._compiler_profile)

      with self.context.state('classpath', []) as cp:
        for conf in self._confs:
          cp.insert(0, (conf, self._classes_dir))

        with self.changed(java_targets, invalidate_dependants=True) as changed:
          sources_by_target, processors, fingerprint = self.calculate_sources(changed)
          if sources_by_target:
            sources = reduce(lambda all_, sources: all_.union(sources), sources_by_target.values())
            if not sources:
              self.context.log.warn('Skipping java compile for targets with no sources:\n  %s' %
                                    '\n  '.join(str(t) for t in sources_by_target.keys()))
            else:
              classpath = [jar for conf, jar in cp if conf in self._confs]
              result = self.compile(jmake_classpath, compiler_classpath, classpath, sources,
                                    fingerprint)
              if result != 0:
                task_error_msg = 'java %s ... exited non-zero (%i)' % (_JMAKE_MAIN, result)
                error_msg = _JMAKE_ERROR_CODES.get(result, None)

                if error_msg:
                  task_error_msg += " '%s'" % error_msg
                raise TaskError(task_error_msg)

            if processors:
              # Produce a monolithic apt processor service info file for further compilation rounds
              # and the unit test classpath.
              processor_info_file = os.path.join(self._classes_dir, _PROCESSOR_INFO_FILE)
              if os.path.exists(processor_info_file):
                with safe_open(processor_info_file, 'r') as f:
                  for processor in f:
                    processors.add(processor.strip())
              self.write_processor_info(processor_info_file, processors)

      if self.context.products.isrequired('classes'):
        genmap = self.context.products.get('classes')

        # Map generated classes to the owning targets and sources.
        dependencies = Dependencies(self._classes_dir, self._dependencies_file)
        for target, classes_by_source in dependencies.findclasses(targets).items():
          for source, classes in classes_by_source.items():
            genmap.add(source, self._classes_dir, classes)
            genmap.add(target, self._classes_dir, classes)

        # 'Map' (rewrite) annotation processor service info files to the owning targets.
        for target in targets:
          if is_apt(target) and target.processors:
            basedir = os.path.join(self._resources_dir, target.id)
            processor_info_file = os.path.join(basedir, _PROCESSOR_INFO_FILE)
            self.write_processor_info(processor_info_file, target.processors)
            genmap.add(target, basedir, [_PROCESSOR_INFO_FILE])

  def calculate_sources(self, targets):
    sources = defaultdict(set)
    processors = set()

    def collect_sources(target):
      src = (os.path.join(target.target_base, source)
             for source in target.sources if source.endswith('.java'))
      if src:
        sources[target].update(src)
        if is_apt(target) and target.processors:
          processors.update(target.processors)

    for target in targets:
      collect_sources(target)
    return sources, processors, self.context.identify(targets)

  def compile(self, jmake_classpath, compiler_classpath, classpath, sources, fingerprint):
    safe_mkdir(self._classes_dir)

    opts = [
      '-classpath', ':'.join(classpath),
      '-d', self._classes_dir,
      '-pdb', os.path.join(self._classes_dir, '%s.dependencies.pdb' % fingerprint),
    ]

    opts.extend([
      '-jcpath', ':'.join(compiler_classpath),
      '-jcmainclass', 'com.twitter.common.tools.Compiler',
      '-C-Tdependencyfile', '-C%s' % self._dependencies_file,
    ])
    opts.extend(map(lambda arg: '-C%s' % arg, self._javac_opts))

    opts.extend(self._opts)
    return self.runjava_indivisible(_JMAKE_MAIN, classpath=jmake_classpath, opts=opts, args=sources,
                                    jvmargs=self._jvm_args)

  def write_processor_info(self, processor_info_file, processors):
    with safe_open(processor_info_file, 'w') as f:
      for processor in processors:
        f.write('%s\n' % processor)
